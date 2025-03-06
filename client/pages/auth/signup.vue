<template>
	<form @submit.prevent="onSubmit">
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
		<NuxtLink to="/auth/login">Already have an account?</NuxtLink>
	</form>
	<p v-show="authStore.isSignupError">Signup Error</p>
</template>
<script setup lang="ts">
import * as z from "zod";
import FormInput from "~/components/ui/custom/FormInput.vue";
import { signupValidationSchema } from "~/forms/schemas/signup";

const authStore = useAuthStore();

const { values, errors, defineField, handleSubmit, isSubmitting } = useForm({
	validationSchema: toTypedSchema(signupValidationSchema),
});

const [username, usernameAttrs] = defineField("username");
const [password, passwordAttrs] = defineField("password");
const [firstName, firstNameAttrs] = defineField("firstName");
const [lastName, lastNameAttrs] = defineField("lastName");

const onSubmit = handleSubmit((values) => {
	authStore.signup(values);
});
</script>
