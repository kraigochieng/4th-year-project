<template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>1. Personal Details</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p>Gender</p>
				<p>{{ props.data?.gender }}</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Pregnancy Status</p>
				<p>{{ props.data?.pregnancy_status }}</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Known Allergy</p>
				<p>{{ props.data?.known_allergy }}</p>
			</div>
		</CardContent>
	</Card>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>2. Rechallenge/Dechallenge</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p>Rechallenge</p>
				<p>{{ props.data?.rechallenge }}</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Dechallenge</p>
				<p>{{ props.data?.dechallenge }}</p>
			</div>
		</CardContent>
	</Card>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>3. Grading of the Event</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p>Severity</p>
				<p>{{ props.data?.severity }}</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Is Serious</p>
				<p>{{ props.data?.is_serious }}</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Criteria for Seriousness</p>
				<p>{{ props.data?.criteria_for_seriousness }}</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Action Taken</p>
				<p>{{ props.data?.action_taken }}</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Outcome</p>
				<p>{{ props.data?.outcome }}</p>
			</div>
		</CardContent>
	</Card>
	<div class="flex space-x-2 justify-end">
		<Button @mouseup="router.push(`/adr/${props.data?.id}/edit`)"
			>Edit ADR</Button
		>
		<AlertDialog>
			<AlertDialogTrigger as-child>
				<Button>Delete ADR</Button>
			</AlertDialogTrigger>
			<AlertDialogContent>
				<AlertDialogHeader>
					<AlertDialogTitle>Are you sure?</AlertDialogTitle>
					<AlertDialogDescription>
						This action cannot be undone. This will permanently
						delete this record
					</AlertDialogDescription>
				</AlertDialogHeader>
				<AlertDialogFooter>
					<AlertDialogCancel>Cancel</AlertDialogCancel>
					<AlertDialogAction @mouseup="handleDelete">
						Continue</AlertDialogAction
					>
				</AlertDialogFooter>
			</AlertDialogContent>
		</AlertDialog>
	</div>
</template>

<script setup lang="ts">
import type { ADRGetResponseInterface } from "@/types/adr";

const props = defineProps<{ data?: ADRGetResponseInterface }>();
const router = useRouter();
const authStore = useAuthStore();

async function handleDelete() {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;

	const response = await $fetch(`${serverApi}/adr/${props.data?.id}`, {
		method: "DELETE",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	});

	navigateTo("/adr");
}
</script>
