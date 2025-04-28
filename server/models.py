import datetime
import uuid

from basemodels import (
    ActionTakenEnum,
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelGetResponse,
    CriteriaForSeriousnessEnum,
    DechallengeEnum,
    GenderEnum,
    IsSeriousEnum,
    KnownAllergyEnum,
    OutcomeEnum,
    PregnancyStatusEnum,
    RechallengeEnum,
    ReviewEnum,
    SeverityEnum,
)
from mixins import IDMixin, TimestampMixin
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Uuid,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class MedicalInstitutionModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "medical_institution"

    name = Column(String, nullable=False)
    mfl_code = Column(String, nullable=True)
    dhis_code = Column(String, nullable=True)
    county = Column(String, nullable=False)
    sub_county = Column(String, nullable=False)

    telephones = relationship(
        "MedicalInstitutionTelephoneModel",
        back_populates="medical_institution",
        cascade="all, delete-orphan",
    )

    adrs = relationship("ADRModel", back_populates="medical_institution")


class MedicalInstitutionTelephoneModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "medical_institution_telephone"

    medical_institution_id = Column(
        String, ForeignKey("medical_institution.id", ondelete="CASCADE"), nullable=False
    )
    medical_institution = relationship(
        "MedicalInstitutionModel", back_populates="telephones"
    )

    telephone = Column(String, nullable=False)


class ADRModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "adr"
    # Institution Details
    medical_institution_id = Column(
        String, ForeignKey("medical_institution.id"), nullable=False
    )
    medical_institution = relationship("MedicalInstitutionModel", back_populates="adrs")
    
    # Personal Details
    patient_name = Column(String, nullable=False)
    inpatient_or_outpatient_number = Column(String, nullable=True)
    patient_date_of_birth = Column(Date, nullable=True)
    patient_age = Column(Integer, nullable=True)
    patient_address = Column(String, nullable=True)
    patient_weight_kg = Column(Integer, nullable=True)
    patient_height_cm = Column(Integer, nullable=True)
    ward_or_clinic = Column(String, nullable=True)
    gender = Column(SQLAlchemyEnum(GenderEnum), nullable=False)
    pregnancy_status = Column(SQLAlchemyEnum(PregnancyStatusEnum), nullable=False)
    known_allergy = Column(SQLAlchemyEnum(KnownAllergyEnum), nullable=False)
    # Suspected Adverse Reaction
    date_of_onset_of_reaction = Column(Date, nullable=True)
    description_of_reaction = Column(String, nullable=True)
    # Rechallenge/Dechallenge
    rechallenge = Column(SQLAlchemyEnum(RechallengeEnum), nullable=False)
    dechallenge = Column(SQLAlchemyEnum(DechallengeEnum), nullable=False)
    # Grading of Reaction/Event
    severity = Column(SQLAlchemyEnum(SeverityEnum), nullable=False)
    is_serious = Column(SQLAlchemyEnum(IsSeriousEnum), nullable=False)
    criteria_for_seriousness = Column(
        SQLAlchemyEnum(CriteriaForSeriousnessEnum), nullable=False
    )
    action_taken = Column(SQLAlchemyEnum(ActionTakenEnum), nullable=False)
    outcome = Column(SQLAlchemyEnum(OutcomeEnum), nullable=False)
    # causality_assessment_level = Column(
    #     SQLAlchemyEnum(CausalityAssessmentLevelEnum), nullable=True
    # )
    comments = Column(String, nullable=True)

    # Relationships
    causality_assessment_levels = relationship(
        "CausalityAssessmentLevelModel",
        back_populates="adr",
        cascade="all, delete-orphan",
    )

    # User Tracking
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    user = relationship(
        "UserModel",
        back_populates="adrs",
    )


class CausalityAssessmentLevelModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "causality_assessment_level"

    adr_id = Column(String, ForeignKey("adr.id"), nullable=False)
    adr = relationship(
        "ADRModel",
        back_populates="causality_assessment_levels",
    )

    ml_model_id = Column(
        String,
        nullable=False,
        default="final_ml_model@champion",
    )

    causality_assessment_level_value = Column(
        SQLAlchemyEnum(CausalityAssessmentLevelEnum), nullable=False
    )
    prediction_reason = Column(String, nullable=True)

    reviews = relationship(
        "ReviewModel",
        back_populates="causality_assessment_level",
        cascade="all, delete-orphan",
    )


# ml_model = relationship("MLModelModel", back_populates="causality_assessment_levels")


class ReviewModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "review"

    causality_assessment_level_id = Column(
        String, ForeignKey("causality_assessment_level.id"), nullable=False
    )
    causality_assessment_level = relationship(
        "CausalityAssessmentLevelModel",
        back_populates="reviews",
    )

    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    user = relationship("UserModel", back_populates="reviews")

    approved = Column(Boolean, nullable=False)

    proposed_causality_level = Column(
        SQLAlchemyEnum(CausalityAssessmentLevelEnum), nullable=True
    )

    reason = Column(String, nullable=True)  # Why it was approved


# Add the relationship in ADRModel to allow back-reference to reviews
class UserModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "user"

    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    reviews = relationship(
        "ReviewModel", back_populates="user", cascade="all, delete-orphan"
    )
    adrs = relationship("ADRModel", back_populates="user", cascade="all, delete-orphan")


# class MLModelModel(Base, IDMixin, TimestampMixin):
#     __tablename__ = "ml_model"

#     model = Column(LargeBinary, nullable=False)
#     name = Column(String, nullable=True, unique=True)
#     numerical_columns = Column(String, nullable=False)
#     categorical_columns = Column(String, nullable=False)
#     prediciton_columns = Column(String, nullable=False)
#     one_hot_encoder = Column(LargeBinary, nullable=True)
#     ordinal_encoder = Column(LargeBinary, nullable=True)
#     f1_score = Column(String)
#     f1_score_per_class = Column(String)

#     causality_assessment_levels = relationship(
#         "CausalityAssessmentLevelModel",
#         back_populates="ml_model",
#         cascade="all, delete-orphan",
#     )
