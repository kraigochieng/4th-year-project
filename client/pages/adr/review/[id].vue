<template>
	<p v-if="status == 'pending'">Loading ADR...</p>
	<p v-else-if="status == 'error'">Error {{ error }}</p>
	<div v-else-if="status == 'success'">
		<Accordion type="multiple" class="w-full" :default-value="defaultValue">
			<AccordionItem value="personal-details">
				<AccordionTrigger>Personal Details</AccordionTrigger>
				<AccordionContent>
					<p>Gender: {{ data?.gender }}</p>
					<p>Pregnancy Status: {{ data?.pregnancy_status }}</p>
					<p>Known Allergy: {{ data?.known_allergy }}</p>
				</AccordionContent>
			</AccordionItem>
			<AccordionItem value="rechallenge-dechallenge">
				<AccordionTrigger>Rechallenge/Dechallenge</AccordionTrigger>
				<AccordionContent>
					<p>Rechallenge: {{ data?.rechallenge }}</p>
					<p>Dechallenge: {{ data?.dechallenge }}</p>
				</AccordionContent>
			</AccordionItem>
			<AccordionItem value="grading-of-the-event">
				<AccordionTrigger>Grading of the Event</AccordionTrigger>
				<AccordionContent>
					<p>Severity: {{ data?.severity }}</p>
					<p>Is Serious: {{ data?.is_serious }}</p>
					<p>
						Criteria for Seriousness:
						{{ data?.criteria_for_seriousness }}
					</p>
					<p>Action Taken{{ data?.action_taken }}</p>
					<p>Outcome: {{ data?.outcome }}</p>
				</AccordionContent>
			</AccordionItem>
			<AccordionItem value="review">
				<AccordionTrigger>Review</AccordionTrigger>
				<AccordionContent>
					<ADRReviewForm />
				</AccordionContent>
			</AccordionItem>
		</Accordion>
	</div>
</template>

<script setup lang="ts">
const route = useRoute();
const id = route.params.id as string;
const authStore = useAuthStore();
const defaultValue = [
	"personal-details",
	"rechallenge-dechallenge",
	"grading-of-the-event",
	"review",
];
// const { data, isLoading, isError, error, isSuccess } = useQuery({
// 	queryKey: ["adr", id],
// 	queryFn: () => fetchAdrById(id),
// 	enabled: !!id, // Ensures query runs only if ID is present
// });
const { data, status, error } = useFetch<ADRCreateResponse>(
	`${useRuntimeConfig().public.serverApi}/adr/${id}`,
	{
		method: "GET",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	}
);
</script>
