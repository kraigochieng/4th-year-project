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
		<NuxtLink to="/auth/signup">Create a new account</NuxtLink>
	</form>
	<!-- <div>
		<p>Values {{ values }}</p>
	</div> -->
</template>
<script setup lang="ts">
// Stores
const authStore = useAuthStore();

import FormInput from "~/components/ui/custom/FormInput.vue";

const { values, errors, handleSubmit, defineField, isSubmitting } = useForm({
	validationSchema: toTypedSchema(loginValidationSchema),
});

const [username, usernameAttrs] = defineField("username");
const [password, passwordAttrs] = defineField("password");

const runtimeConfig = useRuntimeConfig();
const serverApi = runtimeConfig.public.serverApi;

const onSubmit = handleSubmit(async (values) => {
	// const {data} = useFetch<TokenResponse>(`${serverApi}/login`, {
	// 	method: "POST",
	// 	body:
	// })

	// const { data } = await postToken(values);
	// if (data.value) {
	// 	localStorage.setItem("accessToken", data.value.accessToken);
	// }
	authStore.login(values)
});
</script>
