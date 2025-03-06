<template>
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
</template>

<script setup lang="ts">
import FormInput from "./ui/custom/FormInput.vue";
import FormRadio from "./ui/custom/FormRadio.vue";
import FormTextArea from "./ui/custom/FormTextArea.vue";
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
</script>
