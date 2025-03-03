import enum
from uuid import UUID

from pydantic import BaseModel


# Define Enums for each field
class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class PregnancyStatusEnum(str, enum.Enum):
    not_applicable = "not applicable"
    not_pregnant = "not pregnant"
    first_trimester = "1st trimester"
    second_trimester = "2nd trimester"
    third_trimester = "3rd trimester"


class KnownAllergyEnum(str, enum.Enum):
    yes = "yes"
    no = "no"


class RechallengeEnum(str, enum.Enum):
    yes = "yes"
    no = "no"
    unknown = "unknown"
    na = "na"


class DechallengeEnum(str, enum.Enum):
    yes = "yes"
    no = "no"
    unknown = "unknown"
    na = "na"


class SeverityEnum(str, enum.Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    fatal = "fatal"
    unknown = "unknown"


class IsSeriousEnum(str, enum.Enum):
    yes = "yes"
    no = "no"


class CriteriaForSeriousnessEnum(str, enum.Enum):
    hospitalisation = "hospitalisation"
    disability = "disability"
    congenital_anomaly = "congenital anomaly"
    life_threatening = "life-threatening"
    death = "death"


class ActionTakenEnum(str, enum.Enum):
    drug_withdrawn = "drug withdrawn"
    dose_reduced = "dose reduced"
    dose_increased = "dose increased"
    dose_not_changed = "dose not changed"
    not_applicable = "not applicable"
    unknown = "unknown"


class OutcomeEnum(str, enum.Enum):
    recovered = "recovered"
    recovered_with_sequelae = "recovered with sequelae"
    recovering = "recovering"
    not_recovered = "not recovered"
    death = "death"
    unknown = "unknown"


class CausalityAssessmentLevelEnum(str, enum.Enum):
    certain = "certain"
    likely = "likely"
    possible = "possible"
    unlikely = "unlikely"
    unclassified = "unclassified"
    unclassifiable = "unclassifiable"


class ReviewEnum(str, enum.Enum):
    approved = "approved"
    denied = "denied"


class ADRBaseModelCreate(BaseModel):
    patient_id: str
    gender: GenderEnum
    pregnancy_status: PregnancyStatusEnum
    known_allergy: KnownAllergyEnum
    rechallenge: RechallengeEnum
    dechallenge: DechallengeEnum
    severity: SeverityEnum
    is_serious: IsSeriousEnum
    criteria_for_seriousness: CriteriaForSeriousnessEnum
    action_taken: ActionTakenEnum
    outcome: OutcomeEnum


class ADRBaseModel(ADRBaseModelCreate):
    id: str | None = None
    causality_assessment_level: CausalityAssessmentLevelEnum | None = None
    prediction_reason: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserSignupBaseModel(BaseModel):
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserDetailsBaseModel(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None


class UserLoginBaseModel(BaseModel):
    username: str
    password: str
