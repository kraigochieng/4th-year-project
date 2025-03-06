<template>
	<form @submit="onSubmit">
		<FormSwitch name="approved" label="Approved" />
		<div v-if="!approved">
			<FormRadio
				name="proposedCausalityLevel"
				label="Proposed Causality Level"
				:options="reviewFormCategoricalValues['proposedCausalityLevel']"
			/>
			<FormTextArea
				name="reason"
				label="Reason"
				placeholder="Enter Reason"
				description="Justification for your proposed causality level"
			/>
		</div>
		<Button type="submit">Submit</Button>
	</form>
</template>

<script setup lang="ts">
const authStore = useAuthStore();
import FormRadio from "./ui/custom/FormRadio.vue";
import FormSwitch from "./ui/custom/FormSwitch.vue";
import FormTextArea from "./ui/custom/FormTextArea.vue";
import humps from "humps";
const route = useRoute();
const id = route.params.id as string; // Get ADR ID from the URL
const {
	values,
	errors,
	defineField,
	handleSubmit,
	isSubmitting,
	setFieldValue,
} = useForm({
	validationSchema: toTypedSchema(reviewFormValidationSchema),
});

const [approved, approvedAttrs] = defineField("approved");
const [proposedCausalityLevel, proposedCausalityLevelAttrs] = defineField(
	"proposedCausalityLevel"
);
const [reason, reasonAttrs] = defineField("reason");

const onSubmit = handleSubmit(async (values) => {
	try {
		const response = await $fetch(
			`${useRuntimeConfig().public.serverApi}/adr/review/${id}`,
			{
				method: "POST",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
					"Content-Type": "application/json",
				},
				body: humps.decamelizeKeys(values), // Sends form values as JSON
			}
		);
		console.log("Form submitted successfully:", response);
		navigateTo("/adr/review");
	} catch (error) {
		console.error("Error submitting form:", error);
	}
});
</script>
