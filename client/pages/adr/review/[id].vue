<template>
	<p v-if="isLoading">Loading ADR...</p>
	<p v-else-if="isError">Error {{ error }}</p>
	<p v-else-if="isSuccess">{{ data }}</p>
	
	
</template>

<script setup lang="ts">
const route = useRoute();
const id = route.params.id as string;

const { data, isLoading, isError, error, isSuccess } = useQuery({
	queryKey: ["adr", id],
	queryFn: () => fetchAdrById(id),
	enabled: !!id, // Ensures query runs only if ID is present
});
</script>
