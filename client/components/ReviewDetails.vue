<template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>Review Details</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p>Vote</p>
				<p><ApprovedBadge :is-approved="data?.approved" /></p>
			</div>
		</CardContent>

		<CardFooter class="card-footer">
			<Button
				@mouseup="
					router.push({
						path: `/causality-assessment-level/${causality_assessment_level_id}/review`,
						query: { mode: 'update' },
					})
				"
			>
				Edit Review
			</Button>
			<AlertDialog>
				<AlertDialogTrigger as-child>
					<Button>Delete Review</Button>
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
							Continue
						</AlertDialogAction>
					</AlertDialogFooter>
				</AlertDialogContent>
			</AlertDialog>
		</CardFooter>
	</Card>
</template>

<script setup lang="ts">
// Props
const props = defineProps<{
	data?: Review;
	causality_assessment_level_id?: string;
}>();

// Stores
const authStore = useAuthStore();

// Routing
const router = useRouter();

// Types
interface Review {
	id: string;
	user_id: string;
	causality_assessment_level?: CausalityAssessmentLevelEnum;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}

// Events
async function handleDelete() {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;

	console.log("button being pressed");
	const response = await $fetch(`${serverApi}/review/${props.data?.id}`, {
		method: "DELETE",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	});

	navigateTo(
		`/causality-assessment-level/${props.causality_assessment_level_id}`
	);
}
</script>

<style scoped>
.card-footer {
	@apply flex space-x-2 justify-end w-full;
}
</style>
