import { defineStore } from "pinia";
import { getCurrentUser, postToken } from "~/api/auth";

interface Credentials {
	username: string;
	password: string;
}

export const useAuthStore = defineStore("auth", () => {
	const accessToken = useCookie("accessToken"); // Persist in cookies
	const refreshToken = useCookie("refreshToken"); // Persist in cookies
	const user = ref();

	async function login(credentials: Credentials) {
		const { status, data, error } = await postToken(credentials);

		if (status.value == "success" && data.value) {
			accessToken.value = data.value.accessToken;
			refreshToken.value = data.value.refreshToken;
			navigateTo("/adr");
		}

		if (status.value == "error") {
			accessToken.value = "";
			refreshToken.value = "";
		}
	}

	function logout() {
		accessToken.value = "";
		refreshToken.value = "";
		user.value = null;
		navigateTo("/auth/login");
	}

	return {
		accessToken,
		refreshToken,
		user,
		login,
		logout,
	};
});
