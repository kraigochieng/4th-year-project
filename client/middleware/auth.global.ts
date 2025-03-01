import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware(async (to, from) => {
	//	Allow access to login and signup pages
	if (to.path === "/auth/login" || to.path === "/auth/signup") return;
	
	const authStore = useAuthStore();

	await nextTick()
	// Redirect to login if not authenticated
	if (useCookie("accessToken").value) {
		return navigateTo("/auth/login");
	}

});

// export default defineNuxtRouteMiddleware((to, from) => {
// 	const accessToken = useCookie("accessToken");

// 	if (!accessToken.value) {
// 		return navigateTo("/auth/login"); // Redirect to login if no token
// 	}
// });