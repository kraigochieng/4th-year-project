<template>
	<form @submit.prevent="onSubmit">
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
		<Button type="submit">Login</Button>
	</form>
	<div>
		<p>Values {{ values }}</p>
	</div>
</template>
<script setup lang="ts">
// Stores

const authStore = useAuthStore();

import * as z from "zod";
import FormInput from "~/components/ui/custom/FormInput.vue";
import { useAuthStore } from "~/stores/auth";
const validationSchema = z.object({
	username: z.string(),
	password: z.string(),
});

const { values, errors, handleSubmit, defineField, isSubmitting } = useForm({
	validationSchema: toTypedSchema(validationSchema),
});

const [username, usernameAttrs] = defineField("username");
const [password, passwordAttrs] = defineField("password");

const onSubmit = handleSubmit((values) => {
	authStore.login(values);
	// if (authStore.accessToken) {
	// 	console.log("success")
	// } else {
	// 	console.log("fail");
	// }
});
</script>
