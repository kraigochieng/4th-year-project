<template>
	<p v-if="calStatus == 'pending'">Loading CAL...</p>
	<p v-else-if="calStatus == 'error'">{{ calError }}</p>
	<div v-else-if="calStatus == 'success'" class="page-wrapper">
		<CausalityAssessmentLevelComparison
			:value="calData?.causality_assessment_level_value"
		/>
		<Tabs default-value="review">
			<div class="w-max mx-auto">
				<TabsList>
					<TabsTrigger value="adr">ADR Details</TabsTrigger>
					<TabsTrigger value="review">Review</TabsTrigger>
				</TabsList>
			</div>

			<TabsContent value="adr">
				<ADRDetails v-if="adrData" :data="adrData" />
			</TabsContent>
			<TabsContent value="review">
				<ADRReviewForm
					:causality_assessment_level_id="calData?.id"
					:mode="mode"
				/>
			</TabsContent>
		</Tabs>
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
	</div>
</template>

<script setup lang="ts">
import type { CausalityAssessmentLevelEnum } from "@/types/adr";

const route = useRoute();
const id = route.params.id as string;

type ModeType = "create" | "update";
const mode: ModeType = (route.query.mode as ModeType) || "create"; // If the mode is not set, then the default is create
// Store
const authStore = useAuthStore();

interface CausalityAssessmentLevel {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	prediction_reason?: string;
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
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
}

// const { data, isLoading, isadrError, adrError, isSuccess } = useQuery({
// 	queryKey: ["adr", id],
// 	queryFn: () => fetchAdrById(id),
// 	enabled: !!id, // Ensures query runs only if ID is present
// });

const calData = ref<CausalityAssessmentLevel | null>(null);
const calError = ref<unknown | null>(null);
const calStatus = ref<"idle" | "pending" | "success" | "error">("idle");

const adrData = ref<ADRFull | null>(null);
const adrError = ref<unknown | null>(null);
const adrStatus = ref<"idle" | "pending" | "success" | "error">("idle");

onMounted(async () => {
	calStatus.value = "pending";
	try {
		const data = await $fetch<CausalityAssessmentLevel>(
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

		if (!data) throw new Error("No causality data received");

		calData.value = data;
		console.log(calData.value.causality_assessment_level_value);
		calStatus.value = "success";
	} catch (error) {
		calError.value = error;
		calStatus.value = "error";
	}
});

// Now separately fetch ADR after calData is set
watchEffect(async () => {
	if (calData.value?.adr_id) {
		adrStatus.value = "pending";
		try {
			const data = await $fetch<ADRFull>(
				`${useRuntimeConfig().public.serverApi}/adr/${
					calData.value.adr_id
				}`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
				}
			);

			if (!data) throw new Error("No ADR data received");

			adrData.value = data;
			adrStatus.value = "success";
		} catch (error) {
			adrError.value = error;
			adrStatus.value = "error";
		}
	}
});

useHead({ title: "Review a Causality Assessment Level | MediLinda" });
</script>
