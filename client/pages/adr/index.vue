<template>
	<div class="container py-8">
		<h1 class="text-2xl font-bold mb-6">ADR Management</h1>

		<ADRDataTable
			:data="data?.items"
			:isLoading="status === 'pending'"
			:currentPage="currentPage"
			:pageSize="pageSize"
			:totalCount="totalCount"
			@viewDetails="handleViewDetails"
			@pageChange="handlePageChange"
			@pageSizeChange="handlePageSizeChange"
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

interface PaginatedADR {
	items?: ADRReviewFull[];
	total: number;
	page: number;
	size: number;
	pages: number;
}

// Fetch ADR Data
const authStore = useAuthStore();

// Create reactive variables for data, status, and error
const data = ref<PaginatedADR | null>(null);
const status = ref<"pending" | "success" | "error">("pending");
const error = ref<string | null>(null);

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(() => data.value?.total || 0);
// Fetch data when component is mounted
onMounted(async () => {
	await fetchADRData();
});

const fetchADRData = async () => {
	try {
		status.value = "pending";
		// Using $fetch for API call
		data.value = await $fetch(
			`${useRuntimeConfig().public.serverApi}/adr`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: currentPage.value,
					size: pageSize.value,
				},
			}
		);

		status.value = "success";
	} catch (err: any) {
		status.value = "error";
		error.value = err.message || "Something went wrong";
	}
};

watch([currentPage, pageSize], () => {
	fetchADRData();
});

// Function to handle viewing details of an ADR
const handleViewDetails = (adr: ADRReviewFull) => {
	// Navigate to details page or open a modal
	console.log("View details for ADR:", adr);
	// You could use router.push(`/adr/${adr.id}`) to navigate to a detail page
};

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};
</script>
