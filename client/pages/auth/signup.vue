<template>
	<form>
		<FormInput
			type="text"
			name="firstName"
			label="First Name"
			placeholder="Enter First Name"
		/>
		<FormInput
			type="text"
			name="lastName"
			label="Last Name"
			placeholder="Enter Last Name"
		/>
		<FormInput
			type="text"
			name="username"
			label="Username"
			placeholder="Enter Username"
		/>
		<FormInput
			type="password"
			name="password"
			label="Password"
			placeholder="Enter Password"
		/>

		<Button type="submit">Sign Up</Button>
	</form>
</template>
<script setup lang="ts">
import * as z from "zod";
import FormInput from "~/components/ui/custom/FormInput.vue";
const validationSchema = z.object({
	username: z.string().min(6),
	password: z.string().min(12),
	firstName: z.string().optional(),
	lastName: z.string().optional(),
});

const { values, errors, defineField, handleSubmit, isSubmitting } = useForm({
	validationSchema: toTypedSchema(validationSchema),
});
</script>
