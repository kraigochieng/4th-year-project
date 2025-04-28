import datetime
import logging
import os
import random
import shutil
from contextlib import asynccontextmanager
from typing import List, Tuple
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
    MedicalInstitutionGetResponse,
    MedicalInstitutionPostRequest,
    MedicalInstitutionTelephoneGetResponse,
    MedicalInstitutionTelephonePostRequest,
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
from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from mlflow.tracking import MlflowClient
from models import (
    ADRModel,
    Base,
    CausalityAssessmentLevelModel,
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
    ReviewModel,
    UserModel,
)
from sklearn.base import BaseEstimator
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload, load_only
from typing_extensions import Annotated

DB_PATH = "db.sqlite"
ADR_CSV_PATH = "data.csv"  # Path to the CSV file
USERS_CSV_PATH = "users.csv"
REVIEWS_CSV_PATH = "reviews.csv"
ARTIFACTS_DIR = f"./{settings.mlflow_model_artifacts_path}"
MEDICAL_INSTITUTION_CSV_PATH = "medical_institutions.csv"

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables once before the app starts
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating tables: {e}")

    session = Session(bind=engine)

    # Add institutions
    institution_count = session.query(MedicalInstitutionModel).count()

    if institution_count == 0 and os.path.exists(MEDICAL_INSTITUTION_CSV_PATH):
        institution_df = pd.read_csv(MEDICAL_INSTITUTION_CSV_PATH)

        institution_entries = []
        for record in institution_df.to_dict(orient="records"):
            institution_entry = MedicalInstitutionModel(
                mfl_code=record["MFL Code"],
                dhis_code=record["DHIS Code"],
                name=record["Name"],
                county=record["County"],
                sub_county=record["Subcounty"],
            )

            institution_entries.append(institution_entry)

        session.add_all(institution_entries)
        session.commit()
        logging.info("Medical Institutions inserted")
    else:
        logging.info("Medical Institutions already inserted")

    # Add telelphones to the institutions
    institution_telephones_count = session.query(
        MedicalInstitutionTelephoneModel
    ).count()

    if institution_telephones_count == 0:
        institutions = session.query(MedicalInstitutionModel).all()

        institution_telephone_entries = []

        for institution in institutions:
            if not institution.telephones:  # If no telephone entries yet
                institution_telephone_entry = MedicalInstitutionTelephoneModel(
                    medical_institution_id=institution.id, telephone="+2547775292595"
                )

                institution_telephone_entries.append(institution_telephone_entry)

        session.add_all(institution_telephone_entries)
        session.commit()

        logging.info("Medical Institution Telephones inserted")
    else:
        logging.info("Medical Institution Telephones already inserted")

    # Add users
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

    # Add ADRs using current user
    adr_count = session.query(ADRModel).count()

    if adr_count == 0 and os.path.exists(ADR_CSV_PATH):
        adr_df = pd.read_csv(ADR_CSV_PATH)

        adr_entries = []
        causality_entries = []

        facility_ids = session.query(MedicalInstitutionModel.id).limit(20).all()
        facility_ids = [id_tuple[0] for id_tuple in facility_ids]

        for record in adr_df.to_dict(orient="records"):
            adr_entry = ADRModel(
                medical_institution_id=random.choice(facility_ids),
                patient_name=record["patient_name"],
                patient_address=record["patient_address"],
                patient_age=record["patient_age"]
                if pd.notna(record["patient_age"])
                else None,
                patient_date_of_birth=datetime.datetime.strptime(
                    record["patient_date_of_birth"], "%Y-%m-%d"
                ).date()
                if pd.notna(record["patient_date_of_birth"])
                else None,
                patient_weight_kg=record["patient_weight_kg"],
                patient_height_cm=record["patient_height_cm"],
                ward_or_clinic=record["ward_or_clinic"],
                inpatient_or_outpatient_number=record["inpatient_or_outpatient_number"],
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
        logging.info("ADR and Causality data already exists. Skipping CSV insertion.")

    # Add reviews
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
    else:
        logging.info("Review data already inserted")
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


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    # lhreje
    return "test"


@app.post("/api/v1/signup", status_code=status.HTTP_201_CREATED)
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


@app.post("/api/v1/token", status_code=status.HTTP_201_CREATED)
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


@app.post("/api/v1/token/refresh", status_code=status.HTTP_201_CREATED)
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


@app.get("/api/v1/users/me", status_code=status.HTTP_201_CREATED)
async def read_users_me(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(UserModel)
        .options(
            load_only(
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
        )
        .filter(UserModel.username == current_user.username)
        .first()
    )

    return db_user


@app.get(
    "/api/v1/adr", response_model=Page[ADRGetResponse], status_code=status.HTTP_200_OK
)
def get_adrs(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    content = db.query(ADRModel)

    return paginate(content)


@app.get("/api/v1/adr/{adr_id}", status_code=status.HTTP_200_OK)
def get_adr_by_id(
    adr_id: str = Path(..., description="ID of ADR to read"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )
    return JSONResponse(content=jsonable_encoder(adr), status_code=status.HTTP_200_OK)


@app.post("/api/v1/adr", status_code=status.HTTP_201_CREATED)
async def post_adr(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    adr: ADRBaseModelCreate,
    db: Session = Depends(get_db),
):
    # Get ML Model
    ml_model = get_ml_model()

    # Get encoders
    one_hot_encoder, ordinal_encoder = get_encoders()

    # Save data as temp df
    temp_df = pd.DataFrame([adr.model_dump()])

    categorical_columns = get_categorical_columns()

    # Encode df
    cat_encoded = one_hot_encoder.transform(temp_df[categorical_columns])
    cat_encoded = pd.DataFrame(
        cat_encoded,
        columns=one_hot_encoder.get_feature_names_out(categorical_columns),
    )

    # Define columns for prediction
    prediction_columns = get_prediction_columns()

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

    # background_data_for_prediction = cat_encoded_background[prediction_columns]

    # # Explain with SHAP
    # explainer = shap.KernelExplainer(
    #     ml_model.predict_proba, background_data_for_prediction
    # )
    # shap_values = explainer.shap_values(prediction_input)

    # print(shap_values)
    # # Convert SHAP explanation to a more understandable format
    # feature_names = prediction_input.columns
    # shap_summary = []

    # # Loop through each class and its corresponding SHAP values
    # for class_index, shap_class_values in enumerate(shap_values):
    #     class_explanation = {
    #         "class": class_index,
    #         "shap_values": [
    #             {"feature": feature, "shap_value": value.item()}
    #             for feature, value in zip(feature_names, shap_class_values)
    #         ],
    #     }
    #     shap_summary.append(class_explanation)

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

    # Get user id
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

    # Add causality assessment level
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
    content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

    return JSONResponse(
        # content={"model": jsonable_encoder(content), "shap": shap_summary},
        content=jsonable_encoder(content),
        status_code=status.HTTP_201_CREATED,
    )


@app.put("/api/v1/adr/{adr_id}", status_code=status.HTTP_200_OK)
async def update_adr(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    updated_adr: ADRBaseModelCreate,
    adr_id: str = Path(..., description="ID of the ADR record to update"),
    db: Session = Depends(get_db),
):
    # Step 1: Get existing ADR record
    adr_model = db.query(ADRModel).filter(ADRModel.id == adr_id).first()
    if not adr_model:
        raise HTTPException(status_code=404, detail="ADR record not found")

    # Step 2: Update ADR fields
    for key, value in updated_adr.model_dump().items():
        setattr(adr_model, key, value)

    db.commit()
    db.refresh(adr_model)

    # Step 3: Load ML model and encoders
    ml_model = get_ml_model()

    one_hot_encoder, ordinal_encoder = get_encoders()

    # Step 4: Create dataframe from updated data
    categorical_columns = get_categorical_columns()

    temp_df = pd.DataFrame([updated_adr.model_dump()])

    # Step 5: Encode data
    cat_encoded = one_hot_encoder.transform(temp_df[categorical_columns])
    cat_encoded = pd.DataFrame(
        cat_encoded, columns=one_hot_encoder.get_feature_names_out(categorical_columns)
    )

    prediction_columns = get_prediction_columns()
    prediction_input = cat_encoded[prediction_columns]

    # Step 6: Predict and decode
    prediction = ml_model.predict(prediction_input)
    decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
        0
    ][0]

    # Step 7: Update causality assessment model
    causality_record = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.adr_id == adr_model.id)
        .first()
    )

    if causality_record:
        causality_record.causality_assessment_level_value = (
            CausalityAssessmentLevelEnum(decoded_prediction)
        )
        db.commit()
        db.refresh(causality_record)
    else:
        new_causality = CausalityAssessmentLevelModel(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum(
                decoded_prediction
            ),
        )
        db.add(new_causality)
        db.commit()
        db.refresh(new_causality)

    # Step 8: Return updated record with causality details
    content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_200_OK,
    )


@app.delete("/api/v1/adr/{adr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adr_by_id(
    adr_id: str = Path(..., description="ID of ADR to delete"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ADR record not found"
        )

    db.delete(adr)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}",
    status_code=status.HTTP_200_OK,
)
async def get_causality_assessment_level_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
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
    status_code=status.HTTP_200_OK,
)
def get_causality_assessment_levels_for_adr(
    adr_id: str = Path(..., description="ID of ADR to read"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )

    content = db.query(CausalityAssessmentLevelModel).filter(
        CausalityAssessmentLevelModel.adr_id == adr_id
    )

    return paginate(content)


@app.delete(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_causality_assessment_level_by_id(
    causality_assessment_level_id: str = Path(..., description="ID of CAL to delete"),
    db: Session = Depends(get_db),
):
    cal = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CAL record not found"
        )

    db.delete(cal)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/review",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    content = db.query(ReviewModel)

    return paginate(content)


@app.get(
    "/api/v1/review_for_specific_user_and_causality_assessment_level",
    status_code=status.HTTP_200_OK,
)
async def get_review_for_specific_user_and_causality_assessment_level(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Query(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    review = (
        db.query(ReviewModel)
        .filter(
            ReviewModel.causality_assessment_level_id == causality_assessment_level_id,
            ReviewModel.user_id == db_user.id,
        )
        .first()
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review


@app.get(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}/review",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_for_causality_assessment_level(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
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


@app.post(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}/review",
    status_code=status.HTTP_201_CREATED,
)
async def post_review(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    review: ADRReviewCreateRequest,
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
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


@app.put("/api/v1/review/{review_id}", status_code=status.HTTP_200_OK)
async def update_review_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    review_update: ADRReviewCreateRequest,
    review_id: str = Path(..., description="ID of review to update"),
    db: Session = Depends(get_db),
):
    # Step 1: Get the existing review
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    # Step 2: Update the fields
    for key, value in review_update.model_dump().items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return JSONResponse(
        content=jsonable_encoder(review),
        status_code=status.HTTP_200_OK,
    )


@app.delete(
    "/api/v1/review/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review_by_id(
    review_id: str = Path(..., description="ID of review to delete"),
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review record not found"
        )

    db.delete(review)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/v1/monitoring", status_code=status.HTTP_200_OK)
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


@app.get(
    "/api/v1/medical_insitutiion",
    response_model=Page[MedicalInstitutionGetResponse],
)
async def get_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    content = db.query(MedicalInstitutionModel)

    return paginate(content)


@app.post("/api/v1/medical_institution", status_code=status.HTTP_201_CREATED)
async def post_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution: MedicalInstitutionPostRequest,
    db: Session = Depends(get_db),
):
    new_institution = MedicalInstitutionModel(**institution.model_dump())

    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)

    return JSONResponse(
        content=jsonable_encoder(new_institution),
        status_code=status.HTTP_201_CREATED,
    )


@app.put("/api/v1/medical_institution/{institution_id}", status_code=status.HTTP_200_OK)
async def update_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution: MedicalInstitutionGetResponse,
    institution_id: str = Path(..., description="ID of Medical Institution to update"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    for key, value in institution.model_dump().items():
        setattr(db_institution, key, value)

    db.commit()
    db.refresh(db_institution)

    return JSONResponse(
        content=jsonable_encoder(db_institution),
        status_code=status.HTTP_200_OK,
    )


@app.delete(
    "/api/v1/medical_institution/{institution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of Medical Institution to delete"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    db.delete(db_institution)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/medical_institution/{institution_id}/telephone",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_telephones_for_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of the Medical Institution"),
    db: Session = Depends(get_db),
):
    # Check if the medical institution exists first (optional but good)
    institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    # Query all telephone numbers for the given institution
    telephones = db.query(MedicalInstitutionTelephoneModel).filter(
        MedicalInstitutionTelephoneModel.medical_institution_id == institution_id
    )

    return paginate(telephones)


@app.get(
    "/api/v1/medical_institution_telephone",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_medical_institution_telephones(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    content = db.query(MedicalInstitutionTelephoneModel)
    return paginate(content)


@app.post("/api/v1/medical_institution_telephone", status_code=status.HTTP_201_CREATED)
async def create_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    telephone: MedicalInstitutionTelephonePostRequest,
    db: Session = Depends(get_db),
):
    new_telephone = MedicalInstitutionTelephoneModel(**telephone.model_dump())

    db.add(new_telephone)
    db.commit()
    db.refresh(new_telephone)

    return JSONResponse(
        content=jsonable_encoder(new_telephone),
        status_code=status.HTTP_201_CREATED,
    )


@app.put(
    "/api/v1/medical_institution_telephone/{telephone_id}",
    status_code=status.HTTP_200_OK,
)
async def update_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    telephone_update: MedicalInstitutionTelephonePostRequest,
    telephone_id: str = Path(..., description="ID of Telephone record to update"),
    db: Session = Depends(get_db),
):
    db_telephone = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(MedicalInstitutionTelephoneModel.id == telephone_id)
        .first()
    )

    if not db_telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telephone record not found",
        )

    for key, value in telephone_update.model_dump().items():
        setattr(db_telephone, key, value)

    db.commit()
    db.refresh(db_telephone)

    return JSONResponse(
        content=jsonable_encoder(db_telephone),
        status_code=status.HTTP_200_OK,
    )


@app.delete(
    "/api/v1/medical_institution_telephone/{telephone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    telephone_id: str = Path(..., description="ID of Telephone record to delete"),
    db: Session = Depends(get_db),
):
    db_telephone = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(MedicalInstitutionTelephoneModel.id == telephone_id)
        .first()
    )

    if not db_telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telephone record not found",
        )

    db.delete(db_telephone)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def get_ml_model() -> BaseEstimator:
    """Load the trained ML model."""
    model_path = f"{settings.mlflow_model_artifacts_path}/model/model.pkl"
    return joblib.load(model_path)


def get_encoders() -> Tuple[OneHotEncoder, OrdinalEncoder]:
    """Load the one-hot and ordinal encoders."""
    encoders_path = f"{settings.mlflow_model_artifacts_path}/encoders"
    one_hot_encoder = joblib.load(f"{encoders_path}/one_hot_encoder.pkl")
    ordinal_encoder = joblib.load(f"{encoders_path}/ordinal_encoder.pkl")
    return one_hot_encoder, ordinal_encoder


def get_categorical_columns() -> List[str]:
    """Return list of categorical fields used for encoding."""
    return [
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


def get_prediction_columns() -> List[str]:
    """Return list of columns used as prediction features after encoding."""
    return [
        "rechallenge_yes",
        "rechallenge_no",
        "rechallenge_unknown",
        "rechallenge_na",
        "dechallenge_yes",
        "dechallenge_no",
        "dechallenge_unknown",
        "dechallenge_na",
    ]
