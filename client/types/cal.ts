export interface CausalityAssessmentLevelGetResponseInterface {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	prediction_reason: string;
	created_at: string;
	updated_at: string;
}
