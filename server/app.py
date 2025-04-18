import datetime
import logging
import os
import random
import shutil
from contextlib import asynccontextmanager
from typing import List
from uuid import uuid4

import boto3
import joblib
import jwt
import mlflow
import pandas as pd
import shap
from auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from basemodels import (
    ActionTakenEnum,
    ADRBaseModel,
    ADRBaseModelCreate,
    ADRCreateRequest,
    ADRCreateResponse,
    ADRGetResponse,
    ADRReviewCreateRequest,
    ADRReviewGetResponse,
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelGetResponse2,
    CriteriaForSeriousnessEnum,
    DechallengeEnum,
    GenderEnum,
    IsSeriousEnum,
    KnownAllergyEnum,
    OutcomeEnum,
    PregnancyStatusEnum,
    RechallengeEnum,
    ReviewGetResponse,
    SeverityEnum,
    Token,
    UserDetailsBaseModel,
    UserGetResponse,
    UserSignupBaseModel,
)
from config import settings
from dependencies import get_db
from engines import engine
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from mlflow.tracking import MlflowClient
from models import ADRModel, Base, CausalityAssessmentLevelModel, ReviewModel, UserModel
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload
from typing_extensions import Annotated

DB_PATH = "db.sqlite"
ADR_CSV_PATH = "data.csv"  # Path to the CSV file
USERS_CSV_PATH = "users.csv"
REVIEWS_CSV_PATH = "reviews.csv"
ARTIFACTS_DIR = f"./{settings.mlflow_model_artifacts_path}"

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables once before the app starts
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating tables: {e}")

    session = Session(bind=engine)

    user_count = session.query(UserModel).count()

    if user_count == 0 and os.path.exists(USERS_CSV_PATH):
        users_df = pd.read_csv(USERS_CSV_PATH)
        session.bulk_insert_mappings(UserModel, users_df.to_dict(orient="records"))
        session.commit()
        logging.info("User data inserted successfully.")
    else:
        logging.info("User data already exists. Skipping CSV insertion.")

    # Retrieve User ID for username "A"
    user_a = session.query(UserModel).filter(UserModel.username == "A").first()

    if not user_a:
        logging.error("User with username 'A' not found! ADR insertion aborted.")
        session.close()
        yield
        return

    user_a_id = user_a.id  # Get user ID

    adr_count = session.query(ADRModel).count()

    if adr_count == 0 and os.path.exists(ADR_CSV_PATH):
        adr_df = pd.read_csv(ADR_CSV_PATH)

        adr_entries = []
        causality_entries = []

        for record in adr_df.to_dict(orient="records"):
            adr_entry = ADRModel(
                patient_id=record["patient_id"],
                user_id=user_a_id,
                gender=GenderEnum(record["gender"]),
                pregnancy_status=PregnancyStatusEnum(record["pregnancy_status"]),
                known_allergy=KnownAllergyEnum(record["known_allergy"]),
                rechallenge=RechallengeEnum(record["rechallenge"]),
                dechallenge=DechallengeEnum(record["dechallenge"]),
                severity=SeverityEnum(record["severity"]),
                is_serious=IsSeriousEnum(record["is_serious"]),
                criteria_for_seriousness=CriteriaForSeriousnessEnum(
                    record["criteria_for_seriousness"]
                ),
                action_taken=ActionTakenEnum(record["action_taken"]),
                outcome=OutcomeEnum(record["outcome"]),
            )
            adr_entries.append(adr_entry)

        session.add_all(adr_entries)
        session.commit()  # This assigns IDs via flush

        logging.info("ADR inserted successfully.")
        # Now that adr_entries have IDs, link them to causality entries
        for adr_entry, record in zip(adr_entries, adr_df.to_dict(orient="records")):
            causality_entry = CausalityAssessmentLevelModel(
                adr_id=adr_entry.id,
                ml_model_id="final_ml_model@champion",
                causality_assessment_level_value=CausalityAssessmentLevelEnum(
                    record["causality_assessment_level"]
                ),
                prediction_reason=None,
            )
            causality_entries.append(causality_entry)

        session.add_all(causality_entries)
        session.commit()

        logging.info("Causality Assessment inserted successfully.")
    else:
        logging.info("ADR data already exists. Skipping CSV insertion.")

    review_count = session.query(ReviewModel).count()

    if review_count == 0:
        causality_entries = session.query(CausalityAssessmentLevelModel).limit(20).all()
        users = session.query(UserModel).all()
        user_ids = [u.id for u in users]

        for causality_entry in causality_entries:
            # Ensure 20 unique users per causality assessment
            selected_user_ids = random.sample(user_ids, min(20, len(user_ids)))

            for user_id in selected_user_ids:
                approved = random.choice([True, False])
                proposed_level = (
                    random.choice(list(CausalityAssessmentLevelEnum))
                    if not approved
                    else None
                )
                reason = (
                    random.choice(
                        [
                            "Sufficient evidence provided.",
                            "Missing key symptom analysis.",
                            "Reviewed and agreed.",
                            "Contradicts known patterns.",
                            "Needs expert second opinion.",
                            "",
                        ]
                    )
                    if not approved
                    else None
                )

                review = ReviewModel(
                    causality_assessment_level_id=causality_entry.id,
                    user_id=user_id,
                    approved=approved,
                    proposed_causality_level=proposed_level,
                    reason=reason,
                )
                session.add(review)

        session.commit()
        logging.info("Random reviews for first 20 causality assessments inserted.")

    # if adr_count == 0 and os.path.exists(ADR_CSV_PATH):
    #     adr_df = pd.read_csv(ADR_CSV_PATH)
    #     adr_records = adr_df.to_dict(orient="records")
    #     for record in adr_records:
    #         record["user_id"] = user_a_id  # Assign retrieved user_id

    #     session.bulk_insert_mappings(ADRModel, adr_records)
    #     session.commit()
    #     logging.info("ADR data inserted successfully.")
    # else:
    #     logging.info("ADR data already exists. Skipping CSV insertion.")

    session.close()

    if not os.path.exists(ARTIFACTS_DIR):
        try:
            logging.info("Downloading ML Model Artifacts")

            # Tracking URI
            mlflow.set_tracking_uri(
                f"http://{settings.mlflow_tracking_server_host}:{settings.mlflow_tracking_server_port}"
            )

            # Credentials
            # Set MinIO Credentials
            os.environ["AWS_ACCESS_KEY_ID"] = settings.minio_access_key
            os.environ["AWS_SECRET_ACCESS_KEY"] = settings.minio_secret_access_key
            os.environ["AWS_DEFAULT_REGION"] = settings.aws_region

            os.environ["MLFLOW_S3_ENDPOINT_URL"] = (
                f"http://{settings.minio_host}:{settings.minio_api_port}"
            )

            # Test if credentials are set correctly
            boto3.client(
                "s3",
                endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL"),
            )

            mlflow_client = MlflowClient()

            ml_model_version = mlflow_client.get_model_version_by_alias(
                settings.mlflow_model_name, settings.mlflow_model_alias
            )

            ml_model_run_id = ml_model_version.run_id

            logging.info(
                f"✅ Retrieved model version {ml_model_version.version} (run_id: {ml_model_run_id})"
            )

            # 2️⃣ List available artifacts
            artifacts = mlflow_client.list_artifacts(ml_model_run_id)
            if not artifacts:
                logging.warning("No artifacts found for this model.")
            else:
                logging.info(
                    f"Available artifacts: {[artifact.path for artifact in artifacts]}"
                )

            # 3️⃣ Ensure local artifacts directory exists
            os.makedirs(ARTIFACTS_DIR, exist_ok=True)
            mlflow_client.download_artifacts(
                ml_model_run_id,
                "",
                dst_path=ARTIFACTS_DIR,
            )
            logging.info("Downloaded ML Model Artifacts")

        except Exception as e:
            logging.error(f"Error during ML model retrieval: {e}")

    else:
        logging.info("Skipping artifact download")
    yield

    # Delete the SQLite database after shutdown
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            logging.info("Database deleted successfully.")
        except Exception as e:
            logging.error(f"Error deleting database: {e}")

    # Delete the SQLite database after shutdown
    if os.path.exists(ARTIFACTS_DIR):
        try:
            shutil.rmtree(ARTIFACTS_DIR)
            logging.info("Artifacts deleted successfully.")
        except Exception as e:
            logging.error(f"Error deleting artifacts: {e}")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)


@app.get("/")
def root():
    # lhreje
    return "test"


@app.post("/api/v1/signup")
async def signup(user: UserSignupBaseModel, db: Session = Depends(get_db)):
    existing_user = (
        db.query(UserModel).filter(UserModel.username == user.username).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    new_user = UserModel(
        username=user.username,
        password=get_password_hash(user.username),
        first_name=user.first_name,
        last_name=user.last_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_basemodel = UserDetailsBaseModel(
        id=new_user.id,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
    )
    return JSONResponse(
        content=jsonable_encoder(user_basemodel), status_code=status.HTTP_200_OK
    )


@app.post("/api/v1/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    existing_user = (
        db.query(UserModel).filter(UserModel.username == form_data.username).first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(
        minutes=settings.server_access_token_expire_minutes
    )

    access_token = create_access_token(
        data={"sub": existing_user.username}, expires_delta=access_token_expires
    )

    refresh_token_expires = datetime.timedelta(
        days=settings.server_refresh_token_expire_days
    )

    refresh_token = create_refresh_token(
        data={"sub": existing_user.username}, expires_delta=refresh_token_expires
    )

    return JSONResponse(
        content=jsonable_encoder(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        ),
        status_code=status.HTTP_200_OK,
    )


@app.post("/api/v1/token/refresh")
async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.server_refresh_secret_key,
            algorithms=[settings.server_refresh_algorithm],
        )
        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Generate new access token
        new_access_token = create_access_token(
            data={"sub": username},
            expires_delta=datetime.timedelta(
                minutes=settings.server_access_token_expire_minutes
            ),
        )
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@app.get("/api/v1/users/me")
async def read_users_me(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
):
    return current_user


@app.get("/api/v1/adr", response_model=Page[ADRGetResponse])
def get_adrs(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    content = db.query(ADRModel).options(
        joinedload(ADRModel.causality_assessment_levels).joinedload(
            CausalityAssessmentLevelModel.reviews
        )
    )

    return paginate(content)


@app.get("/api/v1/adr/{adr_id}")
def get_adr_by_id(adr_id: str, db: Session = Depends(get_db)):
    adr = (
        db.query(ADRModel)
        .options(joinedload(ADRModel.causality_assessment_levels))
        .filter(ADRModel.id == adr_id)
        .first()
    )

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )
    return JSONResponse(content=jsonable_encoder(adr), status_code=status.HTTP_200_OK)


@app.post("/api/v1/adr")
async def post_adr(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    adr: ADRBaseModelCreate,
    db: Session = Depends(get_db),
):
    # Get ML Model
    ml_model_path = f"{settings.mlflow_model_artifacts_path}/model/model.pkl"
    ml_model = joblib.load(ml_model_path)

    # Get encoders
    encoders_path = f"{settings.mlflow_model_artifacts_path}/encoders"
    one_hot_encoder: OneHotEncoder = joblib.load(f"{encoders_path}/one_hot_encoder.pkl")
    ordinal_encoder: OrdinalEncoder = joblib.load(
        f"{encoders_path}/ordinal_encoder.pkl"
    )

    # Save data as temp df
    temp_df = pd.DataFrame([adr.model_dump()])
    categorical_columns = [
        "gender",
        "pregnancy_status",
        "known_allergy",
        "rechallenge",
        "dechallenge",
        "severity",
        "is_serious",
        "criteria_for_seriousness",
        "action_taken",
        "outcome",
    ]

    # Encode df
    cat_encoded = one_hot_encoder.transform(temp_df[categorical_columns])
    cat_encoded = pd.DataFrame(
        cat_encoded,
        columns=one_hot_encoder.get_feature_names_out(categorical_columns),
    )

    # Preprocess Background data (To be done by you GPT, do the encoding)

    # Define columns for prediction
    prediction_columns = [
        "rechallenge_yes",
        "rechallenge_no",
        "rechallenge_unknown",
        "rechallenge_na",
        "dechallenge_yes",
        "dechallenge_no",
        "dechallenge_unknown",
        "dechallenge_na",
    ]

    # Extract prediction input
    prediction_input = cat_encoded[prediction_columns]

    # Predict using the ML model
    prediction = ml_model.predict(prediction_input)

    # Get Background Data
    background_data_csv = "data.csv"
    background_data_df = pd.read_csv(background_data_csv)
    background_data_df = background_data_df[categorical_columns]

    cat_encoded_background = one_hot_encoder.transform(background_data_df)
    cat_encoded_background = pd.DataFrame(
        cat_encoded_background,
        columns=one_hot_encoder.get_feature_names_out(categorical_columns),
    )

    background_data_for_prediction = cat_encoded_background[prediction_columns]

    # Explain with SHAP
    explainer = shap.KernelExplainer(
        ml_model.predict_proba, background_data_for_prediction
    )
    shap_values = explainer.shap_values(prediction_input)

    print(shap_values)
    # Convert SHAP explanation to a more understandable format
    feature_names = prediction_input.columns
    shap_summary = []

    # Loop through each class and its corresponding SHAP values
    for class_index, shap_class_values in enumerate(shap_values):
        class_explanation = {
            "class": class_index,
            "shap_values": [
                {"feature": feature, "shap_value": value.item()}
                for feature, value in zip(feature_names, shap_class_values)
            ],
        }
        shap_summary.append(class_explanation)

    # Decode prediction using ordinal encoder
    decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
        0
    ][0]

    # Add prediction to ADRModel instance
    # adr.causality_assessment_level = CausalityAssessmentLevelEnum(decoded_prediction)
    # Create an ADRBaseModel object using ADRBaseModelCreate fields
    # adr_full = ADRBaseModel(
    #     **adr.model_dump(),
    #     causality_assessment_level=CausalityAssessmentLevelEnum(decoded_prediction),
    # )

    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    adr_model = ADRModel(
        **adr.model_dump(),
        user_id=db_user.id,
    )
    # adr_model.user = current_user
    # adr_model.user_id = current_user.id
    db.add(adr_model)
    db.commit()
    db.refresh(adr_model)

    casuality_assessment_level_model = CausalityAssessmentLevelModel(
        adr_id=adr_model.id,
        causality_assessment_level_value=CausalityAssessmentLevelEnum(
            decoded_prediction
        ),
    )

    db.add(casuality_assessment_level_model)
    db.commit()
    db.refresh(casuality_assessment_level_model)

    # To load the causality assessment levels
    content = (
        db.query(ADRModel)
        .options(joinedload(ADRModel.causality_assessment_levels))
        .filter(ADRModel.id == adr_model.id)
        .first()
    )

    return JSONResponse(
        content={"model": jsonable_encoder(content), "shap": shap_summary},
        status_code=status.HTTP_201_CREATED,
    )


@app.get("/api/v1/causality_assessment_level/{causality_assessment_level_id}")
async def get_causality_assessment_level(
    causality_assessment_level_id: str,
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .options(
            joinedload(CausalityAssessmentLevelModel.reviews)
            .joinedload(ReviewModel.user)
            .load_only(
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
        )
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    approved_count = sum(1 for r in causality_assessment_level.reviews if r.approved)
    not_approved_count = sum(
        1 for r in causality_assessment_level.reviews if not r.approved
    )

    content = {
        **jsonable_encoder(causality_assessment_level),
        "approved_count": approved_count,
        "not_approved_count": not_approved_count,
    }
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
    )


@app.get(
    "/api/v1/adr/{adr_id}/causality_assessment_level",
    response_model=Page[CausalityAssessmentLevelGetResponse2],
)
def get_causality_assessment_levels_for_adr(adr_id: str, db: Session = Depends(get_db)):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )

    content = db.query(CausalityAssessmentLevelModel).filter(
        CausalityAssessmentLevelModel.adr_id == adr_id
    )

    return paginate(content)


@app.post("/api/v1/causality_assessment_level/{causality_assessment_level_id}/review")
async def post_causality_assessment_level_review(
    causality_assessment_level_id: str,
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    review: ADRReviewCreateRequest,
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Causality Level not found"
        )

    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    review_model = ReviewModel(
        **review.model_dump(),
        user_id=db_user.id,
        causality_assessment_level_id=causality_assessment_level_id,
    )

    db.add(review_model)
    db.commit()
    db.refresh(review_model)
    # content = ADRCreateResponse.model_validate(adr_model)
    return JSONResponse(
        content=jsonable_encoder(review_model),
        status_code=status.HTTP_201_CREATED,
    )


@app.get("/api/v1/review")
async def get_adr_reviews(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    skip: int = Query(default=0, alias="offset", ge=0),
    limit: int = Query(default=10, alias="limit", ge=1),
    db: Session = Depends(get_db),
):
    logging.info("Fetching ADRs with reviews...")

    content = (
        db.query(ADRModel)
        .options(
            joinedload(ADRModel.causality_assessment_levels).joinedload(
                CausalityAssessmentLevelModel.reviews
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    # content = db.query(ReviewModel).all()
    logging.info(f"Fetched ADR records: {len(content)}")

    if not content:
        logging.warning("No ADR records found.")
        return []

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


@app.get(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}/review",
    response_model=Page[ReviewGetResponse],
)
async def get_reviews_for_causality_assessment_level(
    causality_assessment_level_id: str,
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    content = (
        db.query(ReviewModel)
        .options(
            joinedload(ReviewModel.user).load_only(
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
        )
        .filter(
            ReviewModel.causality_assessment_level_id == causality_assessment_level_id
        )
    )

    return paginate(content)


@app.get("/api/v1/monitoring")
def get_monitoring(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    start: str = Query(...),
    end: str = Query(...),
    db: Session = Depends(get_db),
):
    # Parse date strings
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").replace(
        tzinfo=datetime.timezone.utc
    )
    # Include the full day by setting end time to 23:59:59.999999
    end_date = (
        datetime.datetime.strptime(end, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc
        )
        + datetime.timedelta(days=1)
        - datetime.timedelta(microseconds=1)
    )

    def query_proportion_data(db: Session, column):
        return (
            db.query(column, func.count(ADRModel.id))
            .filter(ADRModel.created_at >= start_date)
            .filter(ADRModel.created_at <= end_date)
            .group_by(column)
            .all()
        )

    def format_proportion_data(raw_data):
        return {
            "series": [label.value for label, _ in raw_data],
            "data": [count for _, count in raw_data],
        }

    # Gender Proportion
    gender_proportions_data = query_proportion_data(db, ADRModel.gender)
    gender_proportions_content = format_proportion_data(gender_proportions_data)

    # Pregnancy Status Proportion
    pregnancy_status_proportions_data = query_proportion_data(
        db, ADRModel.pregnancy_status
    )
    pregnancy_status_proportions_content = format_proportion_data(
        pregnancy_status_proportions_data
    )

    # Known Allergy Proportion
    known_allergy_proportions_data = query_proportion_data(db, ADRModel.known_allergy)
    known_allergy_proportions_content = format_proportion_data(
        known_allergy_proportions_data
    )

    # Rechallenge Proportion
    rechallenge_proportions_data = query_proportion_data(db, ADRModel.rechallenge)
    rechallenge_proportions_content = format_proportion_data(
        rechallenge_proportions_data
    )

    # Dechallenge Proportion (fixed column name)
    dechallenge_proportions_data = query_proportion_data(db, ADRModel.dechallenge)
    dechallenge_proportions_content = format_proportion_data(
        dechallenge_proportions_data
    )

    # Severity Proportion
    severity_proportions_data = query_proportion_data(db, ADRModel.severity)
    severity_proportions_content = format_proportion_data(severity_proportions_data)

    # Criteria For Seriousness Proportion
    criteria_for_seriousness_proportions_data = query_proportion_data(
        db, ADRModel.criteria_for_seriousness
    )
    criteria_for_seriousness_proportions_content = format_proportion_data(
        criteria_for_seriousness_proportions_data
    )

    # Is Serious Proportion
    is_serious_proportions_data = query_proportion_data(db, ADRModel.is_serious)
    is_serious_proportions_content = format_proportion_data(is_serious_proportions_data)

    # Outcome Proportion
    outcome_proportions_data = query_proportion_data(db, ADRModel.outcome)
    outcome_proportions_content = format_proportion_data(outcome_proportions_data)

    content = {
        "gender_proportions": gender_proportions_content,
        "pregnancy_status_proportions": pregnancy_status_proportions_content,
        "known_allergy_proportions": known_allergy_proportions_content,
        "dechallenge_proportions": dechallenge_proportions_content,
        "rechallenge_proportions": rechallenge_proportions_content,
        "severity_proportions": severity_proportions_content,
        "criteria_for_seriousness_proportions": criteria_for_seriousness_proportions_content,
        "is_serious_proportions": is_serious_proportions_content,
        "outcome_proportions": outcome_proportions_content,
    }

    print(content)

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_200_OK,
    )
