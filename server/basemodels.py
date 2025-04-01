import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


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


class ADRCreateResponse(BaseModel):
    patient_id: str
    user_id: str
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


class ADRCreateRequest(BaseModel):
    patient_id: str
    user_id: str
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


class CausalityAssessmentLevelGetResponse2(BaseModel):
    id: str
    adr_id: str
    ml_model_id: str
    causality_assessment_level_value: CausalityAssessmentLevelEnum
    prediction_reason: str | None = None

class UserGetResponse(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    
class ReviewGetResponse(BaseModel):
    id: str
    causality_assessment_level_id: str
    user_id: str
    user: UserGetResponse
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None




class CausalityAssessmentLevelGetResponse(BaseModel):
    id: str
    adr_id: str
    ml_model_id: str
    causality_assessment_level_value: CausalityAssessmentLevelEnum
    prediction_reason: str | None = None
    reviews: List[ReviewGetResponse] = []


class ADRGetResponse(BaseModel):
    id: str
    patient_id: str
    user_id: str
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
    causality_assessment_levels: List[CausalityAssessmentLevelGetResponse] = []


class ADRBaseModel(ADRBaseModelCreate):
    id: str | None = None
    causality_assessment_level: CausalityAssessmentLevelEnum | None = None
    # prediction_reason: str | None = None


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
    id: str | None = None
    username: str
    first_name: str | None = None
    last_name: str | None = None


class UserLoginBaseModel(BaseModel):
    username: str
    password: str


class ADRReviewCreateRequest(BaseModel):
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None = None


class ADRReviewSchema(BaseModel):
    review_id: str
    user_id: str
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None = None
    created_at: datetime


class ADRReviewGetResponse(BaseModel):
    adr_id: str
    patient_id: str
    user_id: str
    gender: str
    pregnancy_status: str
    known_allergy: str
    rechallenge: str
    dechallenge: str
    severity: str
    is_serious: str
    criteria_for_seriousness: str
    action_taken: str
    outcome: str
    causality_assessment_level: str | None = None
    reviews: List[ADRReviewSchema] = []
