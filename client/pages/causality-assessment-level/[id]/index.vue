<template>
	<Card>
		<CardHeader>
			<CardTitle>ML Model ID</CardTitle>
		</CardHeader>
		<CardContent>
			{{ data?.ml_model_id }}
		</CardContent>
	</Card>
	<Card>
		<CardHeader>
			<CardTitle>Prediction Reason</CardTitle>
		</CardHeader>
		<CardContent>
			{{ data?.prediction_reason }}
		</CardContent>
	</Card>
	{{ data }}
	<ReviewDataTable :data="data?.reviews" />
</template>

<script setup lang="ts">
const route = useRoute();
const id = route.params.id as string;

// Types
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

interface CausalityAssessmentLevel {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	prediction_reason: string;
	reviews: Review[];
	created_at: string;
	updated_at: string;
}

// Fetch ADR Data
const authStore = useAuthStore();
const {
	data,
	status,
	error,
	refresh: refreshData,
} = useFetch<CausalityAssessmentLevel>(
	`${useRuntimeConfig().public.serverApi}/causality_assessment_level/${id}`,
	{
		method: "GET",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	}
);
</script>
