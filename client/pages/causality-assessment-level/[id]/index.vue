<template>
	<div class="page-wrapper">
		<h1 class="text-2xl font-bold mb-6">Specific Causality Assessment</h1>
		<Tabs defaultValue="review">
			<TabsList>
				<TabsTrigger value="cal"
					>Causality Assessment Level Details</TabsTrigger
				>
				<TabsTrigger value="review">Review</TabsTrigger>
			</TabsList>
			<TabsContent value="cal">
				<Card class="my-4">
					<CardHeader>
						<CardTitle>ML Model ID</CardTitle>
					</CardHeader>
					<CardContent>
						{{ causalityAssessmentLevelData?.ml_model_id }}
					</CardContent>
				</Card>
				<!-- <Card class="my-4">
					<CardHeader>
						<CardTitle>Prediction Reason</CardTitle>
					</CardHeader>
					<CardContent>
						{{ causalityAssessmentLevelData?.prediction_reason }}
					</CardContent>
				</Card> -->
				<CausalityAssessmentLevelComparison
					:value="
						causalityAssessmentLevelData?.causality_assessment_level_value
					"
				/>
			</TabsContent>
			<TabsContent value="review">
				<Card :class="[isApproved ? 'bg-green-50' : 'bg-red-50']">
					<CardHeader>
						<CardTitle>Approved Count</CardTitle>
						<CardDescription>The tally of votes</CardDescription>
					</CardHeader>
					<CardContent>
						<div class="flex w-max mx-auto">
							<div class="text-center">
								<p>Approved</p>
								<p class="big-number">
									{{
										causalityAssessmentLevelData?.approved_count
									}}
								</p>
							</div>

							<div
								class="w-[1px] mx-4 bg-slate-200 dark:bg-slate-800"
							></div>

							<div class="text-center">
								<p>Not Approved</p>
								<p class="big-number">
									{{
										causalityAssessmentLevelData?.not_approved_count
									}}
								</p>
							</div>
						</div>
					</CardContent>
				</Card>
				<ReviewDetails
					v-if="currentReviewData"
					:data="currentReviewData"
					:causality_assessment_level_id="id"
				/>
				<div v-if="!currentReviewData">
					<Button
						class="my-4 w-full mx-auto"
						@mouseup="
							router.push(
								`/causality-assessment-level/${id}/review`
							)
						"
						>Add Review</Button
					>
				</div>
				<DataTable
					title="Reviews"
					:data="reviewData?.items"
					:columns="columns"
					:isLoading="reviewStatus === 'pending'"
					:currentPage="currentPage"
					:pageSize="pageSize"
					:totalCount="totalCount"
					@pageChange="handlePageChange"
					@pageSizeChange="handlePageSizeChange"
				/>
			</TabsContent>
		</Tabs>
	</div>
</template>

<script setup lang="ts">
import { TableActionsReview } from "#components";
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import { type ColumnDef } from "@tanstack/vue-table";

const route = useRoute();
const router = useRouter();
const id = route.params.id as string;
const isApproved = computed<boolean>(() => {
	if (
		causalityAssessmentLevelData.value &&
		causalityAssessmentLevelData.value.approved_count >
			causalityAssessmentLevelData.value.not_approved_count
	) {
		return true;
	} else {
		return false;
	}
});
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

const currentReviewData = ref<Review | null>(null);
const currentReviewStatus = ref<"pending" | "success" | "error">("pending");
const currentReviewError = ref<string | null>(null);

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

async function fetchCurrentReviewData() {
	try {
		currentReviewStatus.value = "pending";
		// Using $fetch for API call
		currentReviewData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/review_for_specific_user_and_causality_assessment_level`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					causality_assessment_level_id: id,
				},
			}
		);

		currentReviewStatus.value = "success";
	} catch (err: any) {
		currentReviewStatus.value = "error";
		currentReviewError.value = err.message || "Something went wrong";
	}
}

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(() => reviewData.value?.total || 0);

onMounted(async () => {
	await fetchCausalityAssessmentLevelData();
	await fetchReviewData();
	await fetchCurrentReviewData();
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

const columns: ColumnDef<Review>[] = [
	{
		id: "select",
		header: ({ table }) =>
			h(Checkbox, {
				modelValue:
					table.getIsAllPageRowsSelected() ||
					(table.getIsSomePageRowsSelected() && "indeterminate"),
				"onUpdate:modelValue": (value) =>
					table.toggleAllPageRowsSelected(!!value),
				ariaLabel: "Select all",
			}),
		cell: ({ row }) =>
			h(Checkbox, {
				modelValue: row.getIsSelected(),
				"onUpdate:modelValue": (value) => row.toggleSelected(!!value),
				ariaLabel: "Select row",
			}),
		enableSorting: false,
		enableHiding: false,
	},
	{
		id: "user.first_name",
		accessorKey: "user.first_name",
		header: "First Name",
		cell: ({ row }) => h("div", {}, row.getValue("user.first_name")),
		enableSorting: false,
	},
	{
		id: "user.last_name",
		accessorKey: "user.last_name",
		header: "Last Name",
		cell: ({ row }) => h("div", {}, row.getValue("user.last_name")),
		enableSorting: false,
	},

	{
		id: "approved",
		accessorKey: "approved",
		header: "Approved",
		cell: ({ row }) => h("div", {}, row.getValue("approved")),
		enableSorting: false,
	},
	{
		id: "reason",
		accessorKey: "reason",
		header: "Reason",
		cell: ({ row }) => h("div", {}, row.getValue("reason")),
		enableSorting: false,
	},
	{
		id: "proposed_causality_level",
		accessorKey: "proposed_causality_level",
		header: "Proposed Causality Level",
		cell: ({ row }) =>
			h("div", {}, row.getValue("proposed_causality_level")),
		enableSorting: false,
	},

	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsReview, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];

useHead({ title: "View a Causality Assessment Level | MediLinda" });
</script>

<style scoped>
.big-number {
	@apply text-6xl p-4;
}
</style>
