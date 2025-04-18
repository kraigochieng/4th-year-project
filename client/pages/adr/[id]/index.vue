<template>
	<div class="page-wrapper">
		
		<p v-if="adrStatus == 'pending'">Loading ADR...</p>
		<p v-else-if="adrStatus == 'error'">Error {{ adrError }}</p>
		<div v-else-if="adrStatus == 'success'">
			<!-- <p
			v-for="causality_assessment_level in data?.causality_assessment_levels"
		>
			<Card>
				<CardHeader>
					<CardTitle>Causality Assessment Level</CardTitle>
				</CardHeader>
				<CardContent>
					{{
						causality_assessment_level.causality_assessment_level_value
					}}
				</CardContent>
			</Card>
		</p> -->
			<Card>
				<CardHeader> <CardTitle>Specific ADR</CardTitle> </CardHeader>
				<CardContent>
					<Accordion
						type="multiple"
						class="w-full"
						:default-value="defaultValue"
					>
						<AccordionItem value="personal-details">
							<AccordionTrigger
								>Personal Details</AccordionTrigger
							>
							<AccordionContent :class="accordionContentClass">
								<Card>
									<CardHeader>
										<CardTitle>Gender</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.gender }}
									</CardContent>
								</Card>
								<Card>
									<CardHeader>
										<CardTitle>Pregnancy Status</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.pregnancy_status }}
									</CardContent>
								</Card>
								<Card>
									<CardHeader>
										<CardTitle>Known Allergy</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.known_allergy }}
									</CardContent>
								</Card>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="rechallenge-dechallenge">
							<AccordionTrigger
								>Rechallenge/Dechallenge</AccordionTrigger
							>
							<AccordionContent :class="accordionContentClass">
								<Card>
									<CardHeader>
										<CardTitle>Rechallenge</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.rechallenge }}
									</CardContent>
								</Card>
								<Card>
									<CardHeader>
										<CardTitle>Dechallenge</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.dechallenge }}
									</CardContent>
								</Card>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="grading-of-the-event">
							<AccordionTrigger
								>Grading of the Event</AccordionTrigger
							>
							<AccordionContent :class="accordionContentClass">
								<Card>
									<CardHeader>
										<CardTitle>Severity</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.severity }}
									</CardContent>
								</Card>
								<Card>
									<CardHeader>
										<CardTitle>Is Serious</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.is_serious }}
									</CardContent>
								</Card>
								<Card>
									<CardHeader>
										<CardTitle
											>Criteria For Seriousness</CardTitle
										>
									</CardHeader>
									<CardContent>
										{{ adrData?.criteria_for_seriousness }}
									</CardContent>
								</Card>
								<Card>
									<CardHeader>
										<CardTitle>Action Taken</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.action_taken }}
									</CardContent>
								</Card>
								<Card>
									<CardHeader>
										<CardTitle>Outcome</CardTitle>
									</CardHeader>
									<CardContent>
										{{ adrData?.outcome }}
									</CardContent>
								</Card>
							</AccordionContent>
						</AccordionItem>
						<!-- <AccordionItem value="review">
				<AccordionTrigger>Review</AccordionTrigger>
				<AccordionContent>
					<ADRReviewForm
						:causality_assessment_level_id="
							data?.causality_assessment_levels[0].id
						"
					/>
				</AccordionContent>
			</AccordionItem> -->
					</Accordion>
				</CardContent>
			</Card>

			<DataTable
				title="Causality Assessments"
				:data="causalityAssessmentLevelData?.items"
				:columns="columns"
				:isLoading="causalityAssessmentLevelStatus === 'pending'"
				:currentPage="currentPage"
				:pageSize="pageSize"
				:totalCount="totalCount"
				@pageChange="handlePageChange"
				@pageSizeChange="handlePageSizeChange"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import { TableActionsCausalityAssessmentLevel } from "#components";
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import { type ColumnDef } from "@tanstack/vue-table";

// Get ADR id
const route = useRoute();
const id = route.params.id as string;

// Stores
const authStore = useAuthStore();

// Accordion values to make them open up by default
const defaultValue = [
	"personal-details",
	"rechallenge-dechallenge",
	"grading-of-the-event",
];

const accordionContentClass = "flex gap-4";
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
	created_at: string;
	updated_at: string;
}

interface PaginatedCausalityAssessmentLevel {
	items?: CausalityAssessmentLevel[];
	total: number;
	page: number;
	size: number;
	pages: number;
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
	// causality_assessment_levels: CausalityAssessmentLevel[]; // Array of reviews
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
}

// const { data, isLoading, isError, error, isSuccess } = useQuery({
// 	queryKey: ["adr", id],
// 	queryFn: () => fetchAdrById(id),
// 	enabled: !!id, // Ensures query runs only if ID is present
// });

// const { data, status, error } = useFetch<ADRFull>(
// 	`${useRuntimeConfig().public.serverApi}/adr/${id}/causality_assessment_level`,
// 	{
// 		method: "GET",
// 		headers: {
// 			Authorization: `Bearer ${authStore.accessToken}`,
// 		},
// 	}
// );

const adrData = ref<ADRFull | null>(null);
const adrStatus = ref<"pending" | "success" | "error">("pending");
const adrError = ref<string | null>(null);

const causalityAssessmentLevelData =
	ref<PaginatedCausalityAssessmentLevel | null>(null);
const causalityAssessmentLevelStatus = ref<"pending" | "success" | "error">(
	"pending"
);
const causalityAssessmentLevelError = ref<string | null>(null);

async function fetchADRData() {
	try {
		adrStatus.value = "pending";
		// Using $fetch for API call
		adrData.value = await $fetch(
			`${useRuntimeConfig().public.serverApi}/adr/${id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		adrStatus.value = "success";
	} catch (err: any) {
		adrStatus.value = "error";
		adrError.value = err.message || "Something went wrong";
	}
}

async function fetchCausalityAssessmentLevelData() {
	try {
		causalityAssessmentLevelStatus.value = "pending";
		// Using $fetch for API call
		causalityAssessmentLevelData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/adr/${id}/causality_assessment_level`,
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

		causalityAssessmentLevelStatus.value = "success";
	} catch (err: any) {
		causalityAssessmentLevelStatus.value = "error";
		causalityAssessmentLevelError.value =
			err.message || "Something went wrong";
	}
}

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(
	() => causalityAssessmentLevelData.value?.total || 0
);

onMounted(async () => {
	await fetchADRData();
	await fetchCausalityAssessmentLevelData();
});

watch([currentPage, pageSize], () => {
	fetchCausalityAssessmentLevelData();
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

const columns: ColumnDef<CausalityAssessmentLevel>[] = [
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
		id: "ml_model_id",
		accessorKey: "ml_model_id",
		header: "ML Model ID",
		cell: ({ row }) => h("div", {}, row.getValue("ml_model_id")),
		enableSorting: false,
	},
	{
		id: "causality_assessment_level_value",
		accessorKey: "causality_assessment_level_value",
		header: "Causality Assessment Level",
		cell: ({ row }) =>
			h("div", {}, row.getValue("causality_assessment_level_value")),
	},
	// {
	// 	accessorKey:
	// 		"causality_assessment_levels.causality_assessment_level_value",
	// 	header: "Causality Assessment Level",
	// 	cell: ({ row }) =>
	// 		h(
	// 			"div",
	// 			{},
	// 			row.getValue(
	// 				"causality_assessment_levels"
	// 			)
	// 		),
	// },
	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsCausalityAssessmentLevel, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];
</script>
