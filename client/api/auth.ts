import humps from "humps";
import type { ADRBaseModel } from "~/types/ADR";

interface Credentials {
	username: string;
	password: string;
}

interface UserSignUp {
	username: string;
	password: string;
	firstName?: string;
	lastName?: string;
}

interface RefreshTokenResponse {
	accessToken: string;
	tokenType: string;
}

interface LoginResponse {
	accessToken: string;
	refreshToken: string;
	tokenType: string;
}

function getServerApi() {
	const runtimeConfig = useRuntimeConfig();
	return runtimeConfig.public.serverApi;
}

export async function postToken(credentials: Credentials) {
	const body = new URLSearchParams();

	body.set("username", credentials.username);
	body.set("password", credentials.password);

	return await useFetch<LoginResponse>(`${getServerApi()}/token`, {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
		},
		body: body,
	});
}

export async function postTokenRefresh(refreshToken: string) {
	return await useFetch<RefreshTokenResponse>(
		`${getServerApi()}/token/refresh`,
		{
			method: "POST",
			query: { refreshToken },
		}
	);
}

export async function postSignup(user: UserSignUp) {
	return await useFetch(`${getServerApi()}/signup`, {
		method: "POST",
		body: humps.decamelizeKeys(user),
	});
}

export async function getCurrentUser(accessToken: string) {
	return await useServerFetch(`/users/me`, {
		method: "GET",
		headers: {
			Authorization: `Bearer ${accessToken}`,
		},
	});
}
