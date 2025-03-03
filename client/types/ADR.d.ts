import * as z from "zod";

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
