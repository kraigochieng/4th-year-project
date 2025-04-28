<template>
	<div v-if="isApproved" class="badge bg-green-500">Approved</div>
	<div v-if="!isApproved" class="badge bg-red-500">Not Approved</div>
</template>

<script setup lang="ts">
defineProps<{ isApproved?: boolean }>();
</script>
