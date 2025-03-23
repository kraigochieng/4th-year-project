import datetime
import logging
import os
import shutil
from contextlib import asynccontextmanager
from typing import List

import boto3
import joblib
import jwt
import mlflow
import pandas as pd
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
    ADRReviewCreateRequest,
    ADRReviewGetResponse,
    CausalityAssessmentLevelEnum,
    CriteriaForSeriousnessEnum,
    DechallengeEnum,
    GenderEnum,
    IsSeriousEnum,
    KnownAllergyEnum,
    OutcomeEnum,
    PregnancyStatusEnum,
    RechallengeEnum,
    SeverityEnum,
    Token,
    UserDetailsBaseModel,
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
from mlflow.tracking import MlflowClient
from models import ADRModel, Base, CausalityAssessmentLevelModel, ReviewModel, UserModel
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from typing_extensions import Annotated

DB_PATH = "db.sqlite"
ADR_CSV_PATH = "data.csv"  # Path to the CSV file
USERS_CSV_PATH = "users.csv"
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
                # causality_assessment_level=CausalityAssessmentLevelEnum(record["causality_assessment_level"])
            )
            session.add(adr_entry)
            session.commit()
            session.refresh(adr_entry)  # Retrieve the generated adr_id

            causality_entry = CausalityAssessmentLevelModel(
                adr_id=adr_entry.id,
                ml_model_id="final_ml_model@champion",
                causality_assessment_level_value=CausalityAssessmentLevelEnum(
                    record["causality_assessment_level"]
                ),
                prediction_reason=None,
            )
            session.add(causality_entry)
            session.commit()

        logging.info("ADR and Causality Assessment data inserted successfully.")
    else:
        logging.info("ADR data already exists. Skipping CSV insertion.")

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


@app.get("/api/v1/adr")
def get_all_adrs(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    skip: int = Query(default=0, alias="offset", ge=0),
    limit: int = Query(default=10, alias="limit", ge=1),
    db: Session = Depends(get_db),
):
    logging.info("Fetching ADRs with reviews...")

    # content = (
    #     db.query(ADRModel)
    #     .outerjoin(ReviewModel, ADRModel.id == ReviewModel.adr_id)
    #     .order_by(desc(ReviewModel.created_at))
    #     .all()
    # )

    content = (
        db.query(ADRModel)
        # .join(
        #     CausalityAssessmentLevelModel,
        #     ADRModel.id == CausalityAssessmentLevelModel.adr_id,
        #     isouter=True,
        # )
        # .join(
        #     ReviewModel,
        #     CausalityAssessmentLevelModel.id
        #     == ReviewModel.causality_assessment_level_id,
        #     isouter=True,
        # )
        # .outerjoin(
        #     ReviewModel, ADRModel.id == ReviewModel.adr_id
        # )  # Allow ADRs without reviews
        .options(
            joinedload(ADRModel.causality_assessment_levels).joinedload(
                CausalityAssessmentLevelModel.reviews
            )
        )  # Load levels with ADR
        # .options(
        #     joinedload(CausalityAssessmentLevelModel.reviews)
        # )  # Load reviews with levels
        # .order_by(desc(ReviewModel.created_at))
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

    # print(cat_encoded[prediction_columns])
    # Decide the columns that are required
    # Preprocess the columns decided
    # Predict with the row
    # Save the row
    # Return the row

    # Extract prediction input
    prediction_input = cat_encoded[prediction_columns]

    # Predict using the ML model
    prediction = ml_model.predict(prediction_input)

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
        content=jsonable_encoder(content),
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
        .options(joinedload(CausalityAssessmentLevelModel.reviews))
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )
    return JSONResponse(
        content=jsonable_encoder(causality_assessment_level),
        status_code=status.HTTP_200_OK,
    )


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

    # content = (
    #     db.query(ADRModel)
    #     .outerjoin(ReviewModel, ADRModel.id == ReviewModel.adr_id)
    #     .order_by(desc(ReviewModel.created_at))
    #     .all()
    # )

    content = (
        db.query(ADRModel)
        # .join(
        #     CausalityAssessmentLevelModel,
        #     ADRModel.id == CausalityAssessmentLevelModel.adr_id,
        #     isouter=True,
        # )
        # .join(
        #     ReviewModel,
        #     CausalityAssessmentLevelModel.id
        #     == ReviewModel.causality_assessment_level_id,
        #     isouter=True,
        # )
        # .outerjoin(
        #     ReviewModel, ADRModel.id == ReviewModel.adr_id
        # )  # Allow ADRs without reviews
        .options(
            joinedload(ADRModel.causality_assessment_levels).joinedload(
                CausalityAssessmentLevelModel.reviews
            )
        )  # Load levels with ADR
        # .options(
        #     joinedload(CausalityAssessmentLevelModel.reviews)
        # )  # Load reviews with levels
        # .order_by(desc(ReviewModel.created_at))
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
