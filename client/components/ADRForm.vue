<template>
	<form @submit.prevent="onSubmit">
		<Accordion type="multiple" class="w-full" :default-value="defaultValue">
			<!-- <AccordionItem value="institution-details">
				<AccordionTrigger>Institution Details</AccordionTrigger>
				<AccordionContent>
					
				</AccordionContent>
			</AccordionItem> -->
			<AccordionItem value="personal-details">
				<AccordionTrigger>Personal Details</AccordionTrigger>
				<AccordionContent>
					<!-- <FormInput
						type="text"
						name="patientName"
						label="Patient Name/Initials"
						placeholder="Enter Patient Name"
					/>
					<FormDatePicker
						name="dateOfBirth"
						label="Date Of Birth"
						:value="dateOfBirth"
						:set-field-value="setFieldValue"
					/> -->
					<FormRadio
						name="gender"
						label="Gender"
						:options="adrFormCategoricalValues['gender']"
					/>
					<FormRadio
						name="pregnancyStatus"
						label="Pregnancy Status"
						:options="adrFormCategoricalValues['pregnancyStatus']"
					/>
					<FormRadio
						name="knownAllergy"
						label="Known Allergy"
						:options="adrFormCategoricalValues['knownAllergy']"
					/>
				</AccordionContent>
			</AccordionItem>
			<AccordionItem value="rechallenge-dechallenge">
				<AccordionTrigger>Rechallenge/Dechallenge</AccordionTrigger>
				<AccordionContent>
					<FormRadio
						name="rechallenge"
						label="Rechallenge"
						:options="adrFormCategoricalValues['rechallenge']"
					/>
					<FormRadio
						name="dechallenge"
						label="Dechallenge"
						:options="adrFormCategoricalValues['dechallenge']"
					/>
				</AccordionContent>
			</AccordionItem>
			<AccordionItem value="grading-of-the-event">
				<AccordionTrigger>Grading of the Event</AccordionTrigger>
				<AccordionContent>
					<FormRadio
						name="severity"
						label="Severity"
						:options="adrFormCategoricalValues['severity']"
					/>
					<FormRadio
						name="isSerious"
						label="isSerious"
						:options="adrFormCategoricalValues['isSerious']"
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
				</AccordionContent>
			</AccordionItem>
		</Accordion>

		<Button type="submit">Submit</Button>
	</form>
	<!-- <div>
		<p>Values {{ values }}</p>
		<p>Errors {{ errors }}</p>
	</div> -->
</template>

<script setup lang="ts">
import * as z from "zod";
import humps from "humps";
import FormRadio from "./ui/custom/FormRadio.vue";
const defaultValue = [
	"personal-details",
	"rechallenge-dechallenge",
	"grading-of-the-event",
];
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
const router = useRouter();

// const [patientName, patientNameAttrs] = defineField("patientName");
// const [dateOfBirth, dateOfBirthAttrs] = defineField("dateOfBirth");
const [gender, genderAttrs] = defineField("gender");
const [pregnancyStatus, pregnancyStatusAttrs] = defineField("pregnancyStatus");
const [knownAllergy, knownAllergyAttrs] = defineField("knownAllergy");
const [rechallenge, rechallengeAttrs] = defineField("rechallenge");
const [dechallenge, dechallengeAttrs] = defineField("dechallenge");
const [severity, severityAttrs] = defineField("severity");
const [isSerious, isSeriousAttrs] = defineField("isSerious");
const [criteriaForSeriousness, criteriaForSeriousnessAttrs] = defineField(
	"criteriaForSeriousness"
);
const [actionTaken, actionTakenAttrs] = defineField("actionTaken");
const [outcome, outcomeAttrs] = defineField("outcome");
// const queryClient = useQueryClient();

// const { isPending, isError, error, isSuccess, mutate } = useMutation<
// 	ADRBaseModel,
// 	Error,
// 	typeValidationSchema
// >({
// 	mutationFn: (newAdr) => postAdr(newAdr),
// 	onSuccess: (data, variables, context) => {
// 		queryClient.invalidateQueries({ queryKey: ["adrs"] });
// 		if (data && data.id) {
// 			router.push(`/adr/review/${data.id}`);
// 		} else {
// 			console.error("Mutation response does not contain an ID:", data);
// 		}
// 	},
// });

// function onSubmitSuccess(values: typeValidationSchema) {
// 	// mutate(values);

// }

// function onSubmitError({
// 	values,
// 	errors,
// 	results,
// }: {
// 	values: Partial<typeValidationSchema>;
// 	errors: any;
// 	results: any;
// }) {
// 	console.error(values);
// }

// const onSubmit = handleSubmit(onSubmitSuccess, onSubmitError);

const onSubmit = handleSubmit(async (values) => {
	const runtimeConfig = useRuntimeConfig();
	const authStore = useAuthStore();

	// await nextTick();
	console.log(authStore.accessToken);
	const serverApi = runtimeConfig.public.serverApi;
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

	if (status.value == "success") {
		navigateTo(`/causality-assessment-level/${data.value?.id}/review`);
	}
});
// console.log(data.value);
</script>
