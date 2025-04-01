<template>
	<h1 class="text-2xl font-bold mb-6">Specific Causality Assessment</h1>
	<Card>
		<CardHeader>
			<CardTitle>ML Model ID</CardTitle>
		</CardHeader>
		<CardContent>
			{{ causalityAssessmentLevelData?.ml_model_id }}
		</CardContent>
	</Card>
	<Card>
		<CardHeader>
			<CardTitle>Prediction Reason</CardTitle>
		</CardHeader>
		<CardContent>
			{{ causalityAssessmentLevelData?.prediction_reason }}
		</CardContent>
	</Card>
	<p>Approved: {{ causalityAssessmentLevelData?.approved_count }}</p>
	<p>Not Approved: {{ causalityAssessmentLevelData?.not_approved_count }}</p>
	<ReviewDataTable
		:data="reviewData?.items"
		:isLoading="reviewStatus === 'pending'"
		:currentPage="currentPage"
		:pageSize="pageSize"
		:totalCount="totalCount"
		@pageChange="handlePageChange"
		@pageSizeChange="handlePageSizeChange"
	/>
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

interface PaginatedReview {
	items?: Review[];
	total: number;
	page: number;
	size: number;
	pages: number;
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
	approved_count: number;
	not_approved_count: number;
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

const causalityAssessmentLevelData = ref<CausalityAssessmentLevel | null>(null);
const causalityAssessmentLevelStatus = ref<"pending" | "success" | "error">(
	"pending"
);
const causalityAssessmentLevelError = ref<string | null>(null);

const reviewData = ref<PaginatedReview | null>(null);
const reviewStatus = ref<"pending" | "success" | "error">("pending");
const reviewError = ref<string | null>(null);

async function fetchCausalityAssessmentLevelData() {
	try {
		causalityAssessmentLevelStatus.value = "pending";
		// Using $fetch for API call
		causalityAssessmentLevelData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/causality_assessment_level/${id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		causalityAssessmentLevelStatus.value = "success";
	} catch (err: any) {
		causalityAssessmentLevelStatus.value = "error";
		causalityAssessmentLevelError.value =
			err.message || "Something went wrong";
	}
}

async function fetchReviewData() {
	try {
		reviewStatus.value = "pending";
		// Using $fetch for API call
		reviewData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/causality_assessment_level/${id}/review`,
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

		reviewStatus.value = "success";
	} catch (err: any) {
		reviewStatus.value = "error";
		reviewError.value = err.message || "Something went wrong";
	}
}

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(() => reviewData.value?.total || 0);

onMounted(async () => {
	await fetchCausalityAssessmentLevelData();
	await fetchReviewData();
});

watch([currentPage, pageSize], () => {
	fetchReviewData();
});

// // Function to handle viewing details of an ADR
// const handleViewDetails = (adr: ADRReviewFull) => {
// 	// Navigate to details page or open a modal
// 	console.log("View details for ADR:", adr);
// 	// You could use router.push(`/adr/${adr.id}`) to navigate to a detail page
// };

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};
</script>
