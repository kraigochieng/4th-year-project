<template>
	<div class="fixed top-24 right-4 border rounded-sm bg-white p-2">
		<Popover>
			<PopoverTrigger>
				<Icon name="lucide:menu" />
			</PopoverTrigger>
			<PopoverContent>
				<div>
					<p class="font-semibold">Form Sections</p>
					<p>
						<a href="#institution-details">
							1. Institution Details
						</a>
					</p>
					<p><a href="#patient-details">2. Patient Details</a></p>
					<p>
						<a href="#suspected-adverse-reaction">
							1. Suspected Adverse Reaction
						</a>
					</p>
					<p><a href="#rechallenge">3. Rechallenge/Dechallenge</a></p>
					<p><a href="#grading">3. Grading of the Event</a></p>
					<p>
						<a href="#submit"
							>4.
							{{
								props.mode == "create" ? "Add Adr" : "Edit ADR"
							}}
							Button</a
						>
					</p>
				</div>
			</PopoverContent>
		</Popover>
	</div>
	<form @submit.prevent="onSubmit">
		<Card>
			<CardHeader>
				<CardTitle>
					Add an Adverse Drug Reaction Report (ADR)
				</CardTitle>
				<CardDescription
					>Add an Adverse Drug Reaction Report so that the ML Model
					can predict it</CardDescription
				>
			</CardHeader>
			<CardContent>
				<div class="form-section">
					<p id="institution-details" class="form-section-header">
						1. Institution Details
					</p>
				</div>
				<div class="form-section">
					<p id="patient-details" class="form-section-header">
						2. Patient Details
					</p>
					<FormInput
						type="text"
						name="patientName"
						label="Patient Name"
						placeholder="Patient Name"
						description="The name of the patient"
					/>
					<FormSelectDatePicker
						name="patientDateOfBirth"
						label="Patient Date of Birth"
						description="The patient's birth date"
						v-model="selectedPatientDateOfBirth"
						default-year="2003"
						default-month="9"
						default-day="8"
					/>
					<FormNumberField
						name="patientAge"
						label="Patient Age"
						description="Patient Age in Years"
						:format-options="{
							style: 'unit',
							unit: 'year',
						}"
						v-model="selectedPatientAge"
					/>
					<FormNumberField
						name="patientHeightCm"
						label="Patient Height (in cm)"
						description="Patient Height in centimeters (cm)"
						:format-options="{
							style: 'unit',
							unit: 'centimeter',
						}"
						:min="100"
						v-model="selectedPatientHeightCm"
					/>
					<FormNumberField
						name="patientWeightKg"
						label="Patient Weight (in kg)"
						description="Patient Weight in kilograms (kg)"
						:format-options="{
							style: 'unit',
							unit: 'kilogram',
						}"
						:min="5"
						v-model="selectedPatientWeightKg"
					/>
					<FormInput
						type="text"
						name="inpatientOrOutpatientNumber"
						label="Inpatient/Outpatient Number"
						placeholder="inpatientOrOutpatientNumber"
						description="The inpatient or outpatient number of the patient"
					/>
					<FormInput
						type="text"
						name="patientAddress"
						label="Patient Address"
						placeholder="Patient Address"
						description="The address of the patient"
					/>
					<FormInput
						type="text"
						name="wardOrClinic"
						label="Ward/Clinic"
						placeholder="Ward or Clinic"
						description="The ward or clinic the patient was in"
					/>
					<FormRadio
						name="gender"
						label="Gender"
						:options="adrFormCategoricalValues['gender']"
						description="The gender of the patient"
					/>
					<FormRadio
						name="pregnancyStatus"
						label="Pregnancy Status"
						:options="adrFormCategoricalValues['pregnancyStatus']"
						description="The pregnancy status of the patient"
					/>
					<FormRadio
						name="knownAllergy"
						label="Known Allergy"
						:options="adrFormCategoricalValues['knownAllergy']"
						description="If the patient has a known allergy or not"
					/>
				</div>
				<Separator class="my-4" />
				<div class="form-section">
					<p
						id="suspected-adverse-reaction"
						class="form-section-header"
					>
						3. Suspected Adverse Reaction
					</p>
					<FormSelectDatePicker
						name="dateOfOnsetOfReaction"
						label="Date Of Onset Of Reaction"
						description="The date of onset of reaction"
						v-model="selectedDateOfOnsetOfReaction"
						default-year="2025"
						default-month="1"
						default-day="1"
					/>
					<FormTextArea
						name="descriptionOfReaction"
						label="Description Of Reaction"
						placeholder="Description of Reaction"
						description="The description of the reaction(s) that took place"
					/>
				</div>
				<Separator class="my-4" />
				<div class="form-section">
					<p id="rechallenge" class="form-section-header">
						4. Rechallenge/Dechallenge
					</p>
					<FormRadio
						name="rechallenge"
						label="Rechallenge"
						:options="adrFormCategoricalValues['rechallenge']"
						description="Was the drug reintroduced to after it was previously discontinued due to a suspected ADR?"
					/>
					<FormRadio
						name="dechallenge"
						label="Dechallenge"
						:options="adrFormCategoricalValues['dechallenge']"
						description="Was the drug withdrawed to after it was previously discontinued due to a suspected ADR?"
					/>
				</div>
				<Separator class="my-4" />
				<div class="form-section">
					<p id="grading" class="form-section-header">
						5. Grading of the Event
					</p>
					<FormRadio
						name="severity"
						label="Severity"
						:options="adrFormCategoricalValues['severity']"
						description="Severity"
					/>
					<FormRadio
						name="isSerious"
						label="Is Serious"
						:options="adrFormCategoricalValues['isSerious']"
						description="Is Serious"
					/>
					<FormRadio
						name="criteriaForSeriousness"
						label="Criteria for Seriousness"
						:options="
							adrFormCategoricalValues['criteriaForSeriousness']
						"
					/>
					<FormRadio
						name="actionTaken"
						label="Action Taken"
						:options="adrFormCategoricalValues['actionTaken']"
					/>
					<FormRadio
						name="outcome"
						label="Outcome"
						:options="adrFormCategoricalValues['outcome']"
					/>
				</div>
				<Separator class="my-4" />
				<FormTextArea
					name="comments"
					label="Comments"
					placeholder="Comments"
					description="The comments on the ADR overall"
				/>
			</CardContent>
			<CardFooter>
				<Button id="submit" type="submit" class="w-full mx-auto my-4">{{
					props.mode == "create" ? "Add ADR" : "Edit ADR"
				}}</Button>
			</CardFooter>
		</Card>
	</form>
</template>

<script setup lang="ts">
import humps from "humps";
import * as z from "zod";

import FormInput from "./ui/custom/FormInput.vue";
import FormRadio from "./ui/custom/FormRadio.vue";
import FormSelectDatePicker from "./ui/custom/FormSelectDatePicker.vue";
import FormNumberField from "./ui/custom/FormNumberField.vue";
import FormTextArea from "./ui/custom/FormTextArea.vue";

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

// Lifecycle hooks
onMounted(async () => {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;
	const authStore = useAuthStore();

	// If there is an id
	if (props.id) {
		// Get existing data
		const response = await $fetch<typeValidationSchema>(
			`${serverApi}/adr/${props.id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		// Pre-fill form
		const camel = humps.camelizeKeys(response) as typeValidationSchema;

		for (const key of Object.keys(camel) as Array<
			keyof typeValidationSchema
		>) {
			setFieldValue(key, camel[key]);
		}
	}
});

type typeValidationSchema = z.infer<typeof adrFormValidationSchema>;

const {
	values,
	errors,
	defineField,
	handleSubmit,
	isSubmitting,
	setFieldValue,
} = useForm({
	validationSchema: toTypedSchema(adrFormValidationSchema),
});

// Patient Details
const [patientName, patientNameAttrs] = defineField("patientName");
const [inpatientOrOutpatientNumber, inpatientOrOutpatientNumberAttrs] =
	defineField("inpatientOrOutpatientNumber");
const [patientDateOfBirth, patientDateOfBirthAttrs] =
	defineField("patientDateOfBirth");
const [patientAge, patientAgeAttrs] = defineField("patientAge");
const [patientAddress, patientAddressAttrs] = defineField("patientAddress");
const [patientWeightKg, patientWeightKgAttrs] = defineField("patientWeightKg");
const [patientHeightCm, patientHeightCmAttrs] = defineField("patientHeightCm");
const [wardOrClinic, wardOrClinicAttrs] = defineField("wardOrClinic");
const [gender, genderAttrs] = defineField("gender");
const [pregnancyStatus, pregnancyStatusAttrs] = defineField("pregnancyStatus");
const [knownAllergy, knownAllergyAttrs] = defineField("knownAllergy");
// SuspeCted Adverse Reaction
const [dateOfOnsetOfReaction, dateOfOnsetOfReactionAttrs] = defineField(
	"dateOfOnsetOfReaction"
);
const [descriptionOfReaction, descriptionOfReactionAttrs] = defineField(
	"descriptionOfReaction"
);
// Rechallenge/Dechallenge
const [rechallenge, rechallengeAttrs] = defineField("rechallenge");
const [dechallenge, dechallengeAttrs] = defineField("dechallenge");
// Grading of Event
const [severity, severityAttrs] = defineField("severity");
const [isSerious, isSeriousAttrs] = defineField("isSerious");
const [criteriaForSeriousness, criteriaForSeriousnessAttrs] = defineField(
	"criteriaForSeriousness"
);
const [actionTaken, actionTakenAttrs] = defineField("actionTaken");
const [outcome, outcomeAttrs] = defineField("outcome");
const [comments, commentsAttrs] = defineField("comments");

// V-model for columns
const selectedDateOfOnsetOfReaction = ref<string>("");
const selectedPatientDateOfBirth = ref<string>("");
const selectedPatientAge = ref<number>(18);
const selectedPatientWeightKg = ref<number>(60);
const selectedPatientHeightCm = ref<number>(178);

const months = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
];

// Dates
watchEffect(() => {
	if (selectedPatientDateOfBirth.value) {
		setFieldValue("patientDateOfBirth", selectedPatientDateOfBirth.value);
	} else {
		setFieldValue("patientDateOfBirth", undefined);
	}

	if (selectedPatientAge.value) {
		setFieldValue("patientAge", selectedPatientAge.value);
	} else {
		setFieldValue("patientAge", undefined);
	}

	if (selectedPatientWeightKg.value) {
		setFieldValue("patientWeightKg", selectedPatientWeightKg.value);
	} else {
		setFieldValue("patientWeightKg", undefined);
	}

	if (selectedPatientHeightCm.value) {
		setFieldValue("patientHeightCm", selectedPatientHeightCm.value);
	} else {
		setFieldValue("patientHeightCm", undefined);
	}

	if (selectedDateOfOnsetOfReaction.value) {
		setFieldValue(
			"dateOfOnsetOfReaction",
			selectedDateOfOnsetOfReaction.value
		);
	} else {
		setFieldValue("dateOfOnsetOfReaction", undefined);
	}
});

const onSubmit = handleSubmit(async (values) => {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;
	const authStore = useAuthStore();
	console.log("submitting");
	if (props.mode == "create") {
		const { data, status, error } = await useFetch<ADRCreateResponse>(
			`${serverApi}/adr`,
			{
				method: "POST",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				body: humps.decamelizeKeys(values),
			}
		);

		if (status.value == "success" && data.value) {
			const {
				data: calData,
				status: calStatus,
				error,
			} = await useFetch<PaginatedCausalityAssessmentLevel>(
				`${serverApi}/adr/${data.value.id}/causality_assessment_level`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
					params: {
						page: 1,
						size: 50,
					},
				}
			);

			if (calStatus.value == "success" && calData.value?.items) {
				navigateTo(
					`/causality-assessment-level/${calData.value.items[0].id}/review`
				);
			}
		}
	} else if (props.mode == "update") {
		const { data, status, error } = await useFetch<ADRCreateResponse>(
			`${serverApi}/adr/${props.id}`,
			{
				method: "PUT",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				body: humps.decamelizeKeys(values),
			}
		);

		if (status.value == "success" && data.value) {
			const {
				data: calData,
				status: calStatus,
				error,
			} = await useFetch<PaginatedCausalityAssessmentLevel>(
				`${serverApi}/adr/${data.value.id}/causality_assessment_level`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
					params: {
						page: 1,
						size: 50,
					},
				}
			);

			if (calStatus.value == "success" && calData.value?.items) {
				navigateTo(
					`/causality-assessment-level/${calData.value.items[0].id}/review`
				);
			}
		}
	}
});

const props = defineProps<{
	id?: string;
	mode: "create" | "update";
}>();
</script>
