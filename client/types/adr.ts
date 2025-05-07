export type GenderEnum = "male" | "female";

export type PregnancyStatusEnum =
	| "not applicable"
	| "not pregnant"
	| "1st trimester"
	| "2nd trimester"
	| "3rd trimester";

export type KnownAllergyEnum = "yes" | "no";

export type RechallengeEnum = "yes" | "no" | "unknown" | "na";

export type DechallengeEnum = "yes" | "no" | "unknown" | "na";

export type SeverityEnum = "mild" | "moderate" | "severe" | "fatal" | "unknown";

export type IsSeriousEnum = "yes" | "no";

export type CriteriaForSeriousnessEnum =
	| "hospitalisation"
	| "disability"
	| "congenital anomaly"
	| "life-threatening"
	| "death";

export type ActionTakenEnum =
	| "drug withdrawn"
	| "dose reduced"
	| "dose increased"
	| "dose not changed"
	| "not applicable"
	| "unknown";

export type OutcomeEnum =
	| "recovered"
	| "recovered with sequelae"
	| "recovering"
	| "not recovered"
	| "death"
	| "unknown";

export type CausalityAssessmentLevelEnum =
	| "certain"
	| "likely"
	| "possible"
	| "unlikely"
	| "unclassified"
	| "unclassifiable";

export type ADRBaseModel = {
	id: string;
	patientId: string;
	gender: GenderEnum;
	pregnancyStatus: PregnancyStatusEnum;
	knownAllergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	isSerious: IsSeriousEnum;
	criteriaForSeriousness: CriteriaForSeriousnessEnum;
	actionTaken: ActionTakenEnum;
	outcome: OutcomeEnum;
	causalityAssessmentLevel?: CausalityAssessmentLevelEnum;
	predictionReason?: string;
};

export interface ADRGetResponseInterface {
	id: string;
	medical_institution_id: string;
	// Personal Details
	patient_name: string;
	inpatient_or_outpatient_number?: string;
	patient_date_of_birth?: string;
	patient_age?: number;
	patient_weight_kg?: number;
	patient_height_cm?: number;
	ward_or_clinic?: string;
	gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	// Suspected Adverse Reaction
	date_of_onset_of_reaction?: string;
	description_of_reaction?: string;
	// Rechallenge/Dechallenge
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	// Grading of Reaction/Event
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	comments?: string;
}

export interface ADRCreateResponse {
	id: string;
	patient_id: string;
	user_id: string;
	gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	causality_assessment_level?: CausalityAssessmentLevelEnum;
}

interface ADRReview {
	id: string;
	adr_id: string;
	user_id: string;
	approved: boolean;
	proposed_causality_level: CausalityAssessmentLevelEnum;
	reason: string;
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
}

interface Review {
	id: string;
	user_id: string;
	causality_assessment_level?: CausalityAssessmentLevelEnum;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}

interface ADRReviewFull {
	id: string;
	patient_id: string;
	user_id: string;
	gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	causality_assessment_level: CausalityAssessmentLevelEnum;
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
	reviews: ADRReview[]; // Array of reviews
}

interface ADRFull {
	id: string;
	patient_id: string;
	user_id: string;
	gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
	reviews: Review[]; // Array of reviews
}
