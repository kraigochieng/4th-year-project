<template>
	<form @submit.prevent="onSubmit">
		<Card>
			<CardHeader>
				<CardTitle>
					{{ props.mode == "create" ? "Add" : "Edit" }} an Adverse
					Drug Reaction (ADR) Report
				</CardTitle>
				<CardDescription>
					Add an Adverse Drug Reaction Report so that the ML Model can
					predict it
				</CardDescription>
			</CardHeader>
			<CardContent>
				<div
					class="fixed top-24 right-4 border rounded-sm bg-white p-2"
				>
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
								<p>
									<a href="#patient-details"
										>2. Patient Details</a
									>
								</p>
								<p>
									<a href="#suspected-adverse-reaction">
										3. Suspected Adverse Reaction
									</a>
								</p>
								<p>
									<a href="#rechallenge">
										4. Rechallenge/Dechallenge
									</a>
								</p>
								<p>
									<a href="#grading">
										5. Grading of the Event</a
									>
								</p>
								<p>
									<a href="#submit">
										6.
										{{
											props.mode == "create"
												? "Add Adr"
												: "Edit ADR"
										}}
										Button
									</a>
								</p>
							</div>
						</PopoverContent>
					</Popover>
				</div>
				<div class="form-section">
					<div class="flex items-center gap-x-2">
						<Icon
							name="lucide:hospital"
							class="form-section-header-icon"
						/>
						<p id="institution-details" class="form-section-header">
							1. Institution Details
						</p>
					</div>
					<div class="flex items-center justify-between space-x-2">
						<div class="flex space-x-1">
							<Dialog
								v-model:open="
									isCreateMedicalInstitutionDialogOpen
								"
							>
								<DialogTrigger as-child>
									<span class="underline hover:cursor-pointer"
										>Create</span
									>
								</DialogTrigger>
								<DialogScrollContent>
									<MedicalInstitutionForm
										mode="create"
										:is-in-dialog="true"
										@submitted="
											handleMedicalInstitutionFormSubmitted
										"
									/>
								</DialogScrollContent>
							</Dialog>
							<span>or</span>
							<Dialog>
								<DialogTrigger as-child>
									<span class="underline hover:cursor-pointer"
										>find</span
									>
								</DialogTrigger>
								<DialogScrollContent>
									<DialogHeader>
										<DialogTitle>
											Choose an existing Medical
											Institution
										</DialogTitle>
										<DialogDescription>
											Search for a medical institution
										</DialogDescription>
										<div>
											<Input
												type="text"
												placeholder="Seach for a hospital, minimum 3 characters, by name, MFL Code or location"
												v-model="
													medicalInstitutionSearchInput
												"
											/>
											<div
												v-if="
													medicalInstitutionList &&
													medicalInstitutionList.length >
														0
												"
											>
												<RadioGroup
													v-model="
														medicalInstitutionId
													"
												>
													<div
														v-for="medicalInstitution in medicalInstitutionList"
													>
														<RadioGroupItem
															:id="
																medicalInstitution.id
															"
															:value="
																medicalInstitution.id
															"
														/>
														<Label
															:for="
																medicalInstitution.id
															"
														>
															{{
																medicalInstitution.name
															}}
															|
															{{
																medicalInstitution.mfl_code
															}}</Label
														>
													</div>
												</RadioGroup>
											</div>
											<div
												v-if="
													medicalInstitutionList?.length ==
													0
												"
											>
												No hospitals
											</div>
										</div>
									</DialogHeader>
								</DialogScrollContent>
							</Dialog>
							<span>a Medical Institution</span>
						</div>
					</div>

					<div v-if="medicalInstitutionData">
						<div class="view-details-wrapper">
							<p>Name</p>
							<p>{{ medicalInstitutionData.name }}</p>
						</div>
						<Separator class="my-2" />
						<div class="view-details-wrapper">
							<p>MFL Code</p>
							<p>{{ medicalInstitutionData.mfl_code }}</p>
						</div>
						<Separator class="my-2" />
						<div class="view-details-wrapper">
							<p>DHIS Code</p>
							<p>
								{{ medicalInstitutionData.dhis_code ?? "None" }}
							</p>
						</div>
						<Separator class="my-2" />
						<div class="view-details-wrapper">
							<p>County</p>
							<p>{{ medicalInstitutionData.county ?? "None" }}</p>
						</div>
						<Separator class="my-2" />
						<div class="view-details-wrapper">
							<p>Sub County</p>
							<p>
								{{
									medicalInstitutionData.sub_county ?? "None"
								}}
							</p>
						</div>
					</div>
					<p
						v-if="!medicalInstitutionData"
						class="italic text-gray-400 text-center my-4"
					>
						No medical institution created/chosen
					</p>
				</div>
				<Separator class="my-4" />
				<div class="form-section">
					<div class="flex items-center gap-x-2">
						<Icon
							name="lucide:user-round"
							class="form-section-header-icon"
						/>
						<p id="patient-details" class="form-section-header">
							2. Patient Details
						</p>
					</div>

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
						placeholder="e.g IN-123456, OUT-654321"
						description="The inpatient or outpatient number of the patient"
					/>
					<FormInput
						type="text"
						name="patientAddress"
						label="Patient Address"
						placeholder="e.g Madaraka, Nairobi West, Nairobi"
						description="The address of the patient"
					/>
					<FormInput
						type="text"
						name="wardOrClinic"
						label="Ward/Clinic"
						placeholder="e.g Main Ward"
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

import type { CausalityAssessmentLevelGetResponseInterface } from "@/types/cal";
import type { MedicalInstitutionGetResponseInterface } from "@/types/medical_institution";
import type { PaginatedResponseInterface } from "@/types/pagination";
import FormInput from "./ui/custom/FormInput.vue";
import FormNumberField from "./ui/custom/FormNumberField.vue";
import FormRadio from "./ui/custom/FormRadio.vue";
import FormSelectDatePicker from "./ui/custom/FormSelectDatePicker.vue";
import FormTextArea from "./ui/custom/FormTextArea.vue";

const medicalInstitutionData =
	ref<MedicalInstitutionGetResponseInterface | null>();
const medicalInstitutionList = ref<
	MedicalInstitutionGetResponseInterface[] | null
>();
const medicalInstitutionId = ref<string | undefined>();
const medicalInstitutionSearchInput = ref<string>("");
const isCreateMedicalInstitutionDialogOpen = ref(false);
const authStore = useAuthStore();

watchEffect(async () => {
	if (medicalInstitutionSearchInput.value.length >= 3) {
		console.log(medicalInstitutionSearchInput.value);

		const { data, status, error } = await useFetch<
			PaginatedResponseInterface<MedicalInstitutionGetResponseInterface>
		>(`${useRuntimeConfig().public.serverApi}/medical_institution`, {
			method: "GET",
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
			},
			params: {
				query: medicalInstitutionSearchInput.value,
				size: 10,
			},
		});

		if (data.value?.items) {
			medicalInstitutionList.value = data.value?.items;
		} else {
			medicalInstitutionList.value = [];
		}
	}
});

function handleMedicalInstitutionFormSubmitted(
	success: boolean,
	medicalInstitutionIdFromForm?: string
) {
	if (success) {
		isCreateMedicalInstitutionDialogOpen.value = false; // ✅ Close the dialog only if successful
		medicalInstitutionId.value = medicalInstitutionIdFromForm;
		setFieldValue("medicalInstitutionId", medicalInstitutionId.value);
	} else {
		isCreateMedicalInstitutionDialogOpen.value = true;
	}
}

watchEffect(async () => {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;
	const authStore = useAuthStore();

	if (medicalInstitutionId.value) {
		setFieldValue("medicalInstitutionId", medicalInstitutionId.value);

		const { data, status, error } =
			await useFetch<MedicalInstitutionGetResponseInterface>(
				`${serverApi}/medical_institution/${medicalInstitutionId.value}`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
				}
			);

		medicalInstitutionData.value = data.value;
	}
});

// Lifecycle hooks
onMounted(async () => {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;
	const authStore = useAuthStore();

	// If there is an id
	if (props.id) {
		// Get existing data
		const response = await $fetch<adrFormTypeValidationSchema>(
			`${serverApi}/adr/${props.id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		// Pre-fill form
		const camel = humps.camelizeKeys(
			response
		) as adrFormTypeValidationSchema;

		for (const key of Object.keys(camel) as Array<
			keyof adrFormTypeValidationSchema
		>) {
			setFieldValue(key, camel[key]);
		}
	}
});

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
			} = await useFetch<
				PaginatedResponseInterface<CausalityAssessmentLevelGetResponseInterface>
			>(`${serverApi}/adr/${data.value.id}/causality_assessment_level`, {
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: 1,
					size: 50,
				},
			});

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
			} = await useFetch<
				PaginatedResponseInterface<CausalityAssessmentLevelGetResponseInterface>
			>(`${serverApi}/adr/${data.value.id}/causality_assessment_level`, {
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: 1,
					size: 50,
				},
			});

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
