<!-- <template>
	<p v-if="status == 'pending'">Loading ADR...</p>
	<p v-else-if="status == 'error'">Error {{ error }}</p>
	<p v-else-if="status == 'success'">{{ data }}</p>
</template>

<script setup lang="ts">
const authStore = useAuthStore();

const { data, status, error } = useFetch<ADRReviewFull[]>(
	`${useRuntimeConfig().public.serverApi}/adr/review`,
	{
		method: "GET",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	}
);
</script> -->
<template>
	<div class="container py-8">
		<h1 class="text-2xl font-bold mb-6">ADR Management</h1>

		<ADRDataTable
			:data="data"
			:isLoading="status === 'pending'"
			@viewDetails="handleViewDetails"
		/>

		<div v-if="error" class="mt-4 p-4 rounded bg-red-100 text-red-800">
			<p>{{ error }}</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { ref } from "vue";
import ADRDataTable from "@/components/ADRDataTable.vue";

// Define the ADR & Review interfaces
interface ADRReview {
	id: string;
	adr_id: string;
	user_id: string;
	approved: boolean;
	proposed_causality_level?: string | null;
	reason?: string | null;
	created_at: string;
	updated_at: string;
}

interface Review {
	id: string;
	user_id: string;
	causality_assessment_level?: CausalityAssessmentLevelEnum
	approved: boolean
	proposed_causality_level?: CausalityAssessmentLevelEnum
	reason?: string
	created_at: string;
	updated_at: string;
}

// interface ADRReviewFull {
// 	id: string;
// 	patient_id: string;
// 	user_id: string;
// 	gender: string;
// 	pregnancy_status: string;
// 	known_allergy: string;
// 	rechallenge: string;
// 	dechallenge: string;
// 	severity: string;
// 	is_serious: string;
// 	criteria_for_seriousness: string;
// 	action_taken: string;
// 	outcome: string;
// 	causality_assessment_level: string;
// 	created_at: string;
// 	updated_at: string;
// 	reviews?: ADRReview[]; // Array of reviews
// }


interface ADRReviewFull {
	id: string;
	patient_id: string;
	user_id: string;
	gender: string;
	pregnancy_status: string;
	known_allergy: string;
	rechallenge: string;
	dechallenge: string;
	severity: string;
	is_serious: string;
	criteria_for_seriousness: string;
	action_taken: string;
	outcome: string;
	created_at: string;
	updated_at: string;
	reviews?: Review[]; // Array of reviews
}
// Fetch ADR Data
const authStore = useAuthStore();
const { data, status, error } = useFetch<ADRReviewFull[]>(
	`${useRuntimeConfig().public.serverApi}/review`,
	{
		method: "GET",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	}
);

console.log(data.value)
console.log(error.value)
// Function to handle viewing details of an ADR
const handleViewDetails = (adr: ADRReviewFull) => {
	// Navigate to details page or open a modal
	console.log("View details for ADR:", adr);
	// You could use router.push(`/adr/${adr.id}`) to navigate to a detail page
};
</script>
