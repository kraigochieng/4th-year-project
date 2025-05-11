<template>
	<div class="page-wrapper">
		<h1 class="text-2xl font-bold mb-6">Specific Causality Assessment</h1>
		<Tabs defaultValue="cal">
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
				<CausalityAssessmentLevelComparison
					:value="
						causalityAssessmentLevelData?.causality_assessment_level_value
					"
				/>
				<Card class="my-4">
					<CardHeader>
						<CardTitle>Class Rankings Using SHAP</CardTitle>
						<CardDescription>Uses SHAP values</CardDescription>
					</CardHeader>
					<CardContent>
						<Table>
							<TableCaption>
								The order of classes and their probabilities of
								being
							</TableCaption>
							<TableHeader>
								<TableRow>
									<TableHead>Rank</TableHead>
									<TableHead>Label</TableHead>
									<TableHead>Base Value</TableHead>
									<TableHead>SHAP Value</TableHead>
									<TableHead>Base + SHAP Value</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								<TableRow
									v-for="(item, index) in classRankings"
								>
									<TableCell> {{ index + 1 }}</TableCell>
									<TableCell>{{
										capitalize(item.label)
									}}</TableCell>
									<TableCell>
										{{ `${item.baseValue.toFixed(4)} %` }}
									</TableCell>
									<TableCell>
										<div class="flex items-center">
											{{
												`${item.shapValue.toFixed(4)} %`
											}}
											<span
												v-if="item.shapValue > 0"
												class="text-green-600"
											>
												<Icon
													name="lucide:arrow-up"
													class="w-4 h-4"
												/>
											</span>
											<span
												v-else-if="item.shapValue < 0"
												class="text-red-600"
											>
												<Icon
													name="lucide:arrow-down"
													class="w-4 h-4"
												/>
											</span>
										</div>
									</TableCell>
									<TableCell>
										{{
											`${item.baseShapValue.toFixed(4)} %`
										}}
									</TableCell>
								</TableRow>
							</TableBody>
						</Table>
					</CardContent>
					<CardFooter class="flex justify-end">
						<Dialog>
							<DialogTrigger as-child>
								<Button
									variant="ghost"
									class="flex items-center"
								>
									<Icon name="lucide:circle-help" />
									<p>Help</p>
								</Button>
							</DialogTrigger>
							<DialogContent>
								<DialogHeader>
									<DialogTitle> Help </DialogTitle>
									<DialogDescription>
										Help
									</DialogDescription>
								</DialogHeader>
								<ul
									class="py-4 text-sm text-neutral-700 dark:text-neutral-400"
								>
									<li>
										<strong>Base Value:</strong> Base Value
									</li>
									<li>
										<strong>SHAP Value:</strong> SHAP Value
									</li>
									<li>
										<strong>Base + SHAP Value:</strong> Base
										+ SHAP
									</li>
								</ul>
							</DialogContent>
						</Dialog>
					</CardFooter>
				</Card>
				<Card class="my-4">
					<CardHeader>
						<CardTitle>
							Feature Rankings Per Class using SHAP
						</CardTitle>
						<CardDescription>
							Feature Rankings Per Class using SHAP
						</CardDescription>
					</CardHeader>
					<CardContent>
						<Tabs
							:default-value="featureRankingsPerClassDefaultTab"
						>
							<TabsList>
								<TabsTrigger
									v-for="(
										classRanking, index
									) in classRankings"
									:value="classRanking.label || ''"
								>
									{{
										`${index + 1}. ${capitalize(
											classRanking.label
										)}`
									}}
								</TabsTrigger>
							</TabsList>
							<TabsContent
								v-for="featureRankingPerClass in featureRankingsPerClass"
								:value="featureRankingPerClass.classLabel || ''"
							>
								<Table>
									<TableCaption>
										{{ featureRankingPerClass.classLabel }}
									</TableCaption>
									<TableHeader>
										<TableRow>
											<TableHead>Feature Name</TableHead>
											<TableHead>Feature Value</TableHead>
											<TableHead>SHAP Value</TableHead>
										</TableRow>
									</TableHeader>
									<TableBody>
										<TableRow
											v-for="feature in featureRankingPerClass.features"
										>
											<TableCell>
												{{ feature.name }}
											</TableCell>
											<TableCell>
												{{ feature.value }}
											</TableCell>
											<TableCell>
												<div class="flex items-center">
													{{
														`${feature.shapValue.toFixed(
															4
														)} %`
													}}
													<span
														v-if="
															feature.shapValue >
															0
														"
														class="text-green-600"
													>
														<Icon
															name="lucide:arrow-up"
															class="w-4 h-4"
														/>
													</span>
													<span
														v-if="
															feature.shapValue <
															0
														"
														class="text-red-600"
													>
														<Icon
															name="lucide:arrow-down"
															class="w-4 h-4"
														/>
													</span>
													<span
														v-if="
															feature.shapValue ==
															0
														"
														class="text-gray-600"
													>
														<Icon
															name="lucide:minus"
															class="w-4 h-4"
														/>
													</span>
												</div>
											</TableCell>
										</TableRow>
									</TableBody>
								</Table>
							</TabsContent>
						</Tabs>
					</CardContent>
				</Card>
			</TabsContent>
			<TabsContent value="review">
				<Card :class="cardBackgroundClass">
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
					>
						Add Review
					</Button>
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
import { capitalize } from "lodash";

import TableActionsReview from "@/components/table/actions/Review.vue";
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import type { CausalityAssessmentLevelWithReviewCountGetResponseInterface } from "@/types/cal";
import type { PaginatedResponseInterface } from "@/types/pagination";
import type {
	ReviewGetResponse,
	ReviewWithUserGetResponse,
} from "@/types/review";
import { type ColumnDef } from "@tanstack/vue-table";

// Routesf
const route = useRoute();
const router = useRouter();
const id = route.params.id as string;

// Computed
const isApproved = computed<"yes" | "no" | "tie">(() => {
	if (
		causalityAssessmentLevelData.value &&
		causalityAssessmentLevelData.value.approved_count >
			causalityAssessmentLevelData.value.not_approved_count
	) {
		return "yes";
	} else if (
		causalityAssessmentLevelData.value &&
		causalityAssessmentLevelData.value.approved_count <
			causalityAssessmentLevelData.value.not_approved_count
	) {
		return "no";
	} else {
		return "tie";
	}
});

const cardBackgroundClass = computed(() => {
	switch (isApproved.value) {
		case "yes":
			return "bg-green-50";
		case "no":
			return "bg-red-50";
		case "tie":
			return "bg-yellow-50";
		default:
			return "";
	}
});

// Fetch ADR Data
const authStore = useAuthStore();

const causalityAssessmentLevelData =
	ref<CausalityAssessmentLevelWithReviewCountGetResponseInterface | null>(
		null
	);
const causalityAssessmentLevelStatus = ref<"pending" | "success" | "error">(
	"pending"
);
const causalityAssessmentLevelError = ref<string | null>(null);

const reviewData =
	ref<PaginatedResponseInterface<ReviewWithUserGetResponse> | null>(null);
const reviewStatus = ref<"pending" | "success" | "error">("pending");
const reviewError = ref<string | null>(null);

const currentReviewData = ref<ReviewGetResponse | null>(null);
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

// Table
watch([currentPage, pageSize], () => {
	fetchReviewData();
});

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};

const columns: ColumnDef<ReviewWithUserGetResponse>[] = [
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

// Helper Functions
function getClassLabelFromNumber(classNumber: number): string | undefined {
	switch (classNumber) {
		case 0:
			return "certain";
		case 1:
			return "likely";
		case 2:
			return "possible";
		case 3:
			return "unlikely";
		case 4:
			return "unclassified";
		case 5:
			return "unclassifiable";
	}
}

function featureNameFormatter(featureName: string): string | undefined {
	if (featureName == "rechallenge_no") {
		return "Rechallenge (No)";
	} else if (featureName == "rechallenge_na") {
		return "Rechallenge (N/A)";
	} else if (featureName == "rechallenge_yes") {
		return "Rechallenge (Yes)";
	} else if (featureName == "rechallenge_unknown") {
		return "Rechallenge (Unknown)";
	} else if (featureName == "dechallenge_no") {
		return "Dechallenge (No)";
	} else if (featureName == "dechallenge_na") {
		return "Dechallenge (N/A)";
	} else if (featureName == "dechallenge_yes") {
		return "Dechallenge (Yes)";
	} else if (featureName == "dechallenge_unknown") {
		return "Dechallenge (Unknown)";
	}
}

// Computed
const classRankings = computed(() => {
	const data = causalityAssessmentLevelData.value;
	if (!data) return [];

	const baseValues = data.base_values || [];
	const shapValues = data.shap_values_sum_per_class || [];
	const baseShapValues = data.shap_values_and_base_values_sum_per_class || [];

	const rankings = [];
	for (let i = 0; i < baseValues.length; i++) {
		rankings.push({
			label: getClassLabelFromNumber(i),
			baseValue: baseValues[i] * 100,
			shapValue: shapValues[i] * 100,
			baseShapValue: baseShapValues[i] * 100,
		});
	}

	return rankings.sort((a, b) => b.baseShapValue - a.baseShapValue);
});

const DEFAULT_TAB = "certain";
const featureRankingsPerClassDefaultTab = computed(() => {
	// return classRankings.value[0].label;
	// return classRankings.value.length > 0 ? classRankings.value[0].label : "";
	return classRankings.value.length > 0
		? classRankings.value[0].label
		: DEFAULT_TAB;
});

const featureRankingsPerClass = computed(() => {
	const data = causalityAssessmentLevelData.value;
	if (!data) return [];

	const shapMatrix = data.shap_values_matrix as number[][]; // shape: [features][classes]
	const featureNames = data.feature_names as string[];
	const featureValues = data.feature_values as number[];
	const baseValues = data.base_values as number[];
	const numClasses = baseValues.length || 6;
	const numFeatures = shapMatrix.length;

	const result = [];

	for (let classIndex = 0; classIndex < numClasses; classIndex++) {
		const featuresForClass = [];

		for (let featureIndex = 0; featureIndex < numFeatures; featureIndex++) {
			featuresForClass.push({
				name: featureNameFormatter(featureNames[featureIndex]),
				value: featureValues[featureIndex],
				shapValue: shapMatrix[featureIndex][classIndex] * 100,
			});
		}

		// Sort by absolute SHAP value (optional, for top contributors)
		featuresForClass.sort((a, b) => b.shapValue - a.shapValue);

		result.push({
			classLabel: getClassLabelFromNumber(classIndex),
			features: featuresForClass,
		});
	}

	return result;
});

useHead({ title: "View a Causality Assessment Level | MediLinda" });
</script>

<style scoped>
.big-number {
	@apply text-6xl p-4;
}
</style>
