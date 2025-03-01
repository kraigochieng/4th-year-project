import datetime
import logging
import os
from contextlib import asynccontextmanager

import joblib
import jwt
import pandas as pd
from auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from basemodels import (
    ADRBaseModel,
    ADRBaseModelCreate,
    CausalityAssessmentLevelEnum,
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
from models import ADRModel, Base, UserModel
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sqlalchemy.orm import Session
from typing_extensions import Annotated

DB_PATH = "db.sqlite"
ADR_CSV_PATH = "data.csv"  # Path to the CSV file
USERS_CSV_PATH = "users.csv"

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables once before the app starts
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating tables: {e}")

    session = Session(bind=engine)

    adr_count = session.query(ADRModel).count()

    if adr_count == 0 and os.path.exists(ADR_CSV_PATH):
        adr_df = pd.read_csv(ADR_CSV_PATH)
        session.bulk_insert_mappings(ADRModel, adr_df.to_dict(orient="records"))
        session.commit()
        logging.info("ADR data inserted successfully.")
    else:
        logging.info("ADR data already exists. Skipping CSV insertion.")

    user_count = session.query(UserModel).count()

    if user_count == 0 and os.path.exists(USERS_CSV_PATH):
        users_df = pd.read_csv(USERS_CSV_PATH)
        session.bulk_insert_mappings(UserModel, users_df.to_dict(orient="records"))
        session.commit()
        logging.info("User data inserted successfully.")
    else:
        logging.info("User data already exists. Skipping CSV insertion.")

    session.close()

    yield

    # Delete the SQLite database after shutdown
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            logging.info("Database deleted successfully.")
        except Exception as e:
            logging.error(f"Error deleting database: {e}")


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

    return JSONResponse(
        content=jsonable_encoder(new_user), status_code=status.HTTP_200_OK
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
        minutes=settings.access_token_expire_minutes
    )

    access_token = create_access_token(
        data={"sub": existing_user.username}, expires_delta=access_token_expires
    )

    refresh_token_expires = datetime.timedelta(days=settings.refresh_token_expire_days)

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
            settings.refresh_secret_key,
            algorithms=[settings.refresh_algorithm],
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
                minutes=settings.access_token_expire_minutes
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
    content = db.query(ADRModel).offset(skip).limit(limit).all()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


@app.get("/api/v1/adr/{adr_id}")
def get_adr_by_id(adr_id: str, db: Session = Depends(get_db)):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()
    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )
    return JSONResponse(content=jsonable_encoder(adr), status_code=status.HTTP_200_OK)


@app.post("/api/v1/adr")
async def post_adr(adr: ADRBaseModelCreate, db: Session = Depends(get_db)):
    ml_model = joblib.load(settings.ml_model_path)

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
    one_hot_encoder: OneHotEncoder = joblib.load(
        f"{settings.encoders_path}/one_hot_encoder.pkl"
    )
    ordinal_encoder: OrdinalEncoder = joblib.load(
        f"{settings.encoders_path}/ordinal_encoder.pkl"
    )

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
    adr_full = ADRBaseModel(
        **adr.model_dump(),
        causality_assessment_level=CausalityAssessmentLevelEnum(decoded_prediction),
    )

    adr_model = ADRModel(**adr_full.model_dump())
    db.add(adr_model)
    db.commit()
    db.refresh(adr_model)

    return JSONResponse(
        content=jsonable_encoder(adr_model),
        status_code=status.HTTP_201_CREATED,
    )
