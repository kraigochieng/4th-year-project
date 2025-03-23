<template>
	<p v-if="status == 'pending'">Loading ADR...</p>
	<p v-else-if="status == 'error'">Error {{ error }}</p>
	<div v-else-if="status == 'success'">
		<p
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
		</p>
		<Accordion type="multiple" class="w-full" :default-value="defaultValue">
			<AccordionItem value="personal-details">
				<AccordionTrigger>Personal Details</AccordionTrigger>
				<AccordionContent :class="accordionContentClass">
					<Card>
						<CardHeader>
							<CardTitle>Gender</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.gender }}
						</CardContent>
					</Card>
					<Card>
						<CardHeader>
							<CardTitle>Pregnancy Status</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.pregnancy_status }}
						</CardContent>
					</Card>
					<Card>
						<CardHeader>
							<CardTitle>Known Allergy</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.known_allergy }}
						</CardContent>
					</Card>
				</AccordionContent>
			</AccordionItem>
			<AccordionItem value="rechallenge-dechallenge">
				<AccordionTrigger>Rechallenge/Dechallenge</AccordionTrigger>
				<AccordionContent :class="accordionContentClass">
					<Card>
						<CardHeader>
							<CardTitle>Rechallenge</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.rechallenge }}
						</CardContent>
					</Card>
					<Card>
						<CardHeader>
							<CardTitle>Dechallenge</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.dechallenge }}
						</CardContent>
					</Card>
				</AccordionContent>
			</AccordionItem>
			<AccordionItem value="grading-of-the-event">
				<AccordionTrigger>Grading of the Event</AccordionTrigger>
				<AccordionContent :class="accordionContentClass">
					<Card>
						<CardHeader>
							<CardTitle>Severity</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.severity }}
						</CardContent>
					</Card>
					<Card>
						<CardHeader>
							<CardTitle>Is Serious</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.is_serious }}
						</CardContent>
					</Card>
					<Card>
						<CardHeader>
							<CardTitle>Criteria For Seriousness</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.criteria_for_seriousness }}
						</CardContent>
					</Card>
					<Card>
						<CardHeader>
							<CardTitle>Action Taken</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.action_taken }}
						</CardContent>
					</Card>
					<Card>
						<CardHeader>
							<CardTitle>Outcome</CardTitle>
						</CardHeader>
						<CardContent>
							{{ data?.outcome }}
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
		<CausalityAssessmentDataTable
			:data="data?.causality_assessment_levels"
		/>
	</div>
	<p>{{ data?.causality_assessment_levels }}</p>
</template>

<script setup lang="ts">
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
	causality_assessment_levels: CausalityAssessmentLevel[]; // Array of reviews
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
}

// const { data, isLoading, isError, error, isSuccess } = useQuery({
// 	queryKey: ["adr", id],
// 	queryFn: () => fetchAdrById(id),
// 	enabled: !!id, // Ensures query runs only if ID is present
// });

const { data, status, error } = useFetch<ADRFull>(
	`${useRuntimeConfig().public.serverApi}/adr/${id}`,
	{
		method: "GET",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	}
);
</script>
