<template>
	<FormField v-slot="{ componentField }" :name="name">
		<FormItem>
			<FormLabel>{{ label }}</FormLabel>
			<FormControl>
				<Input
					:type="type"
					:placeholder="placeholder"
					v-bind="componentField"
				/>
			</FormControl>
			<FormDescription>
				{{ description }}
			</FormDescription>
			<FormMessage />
		</FormItem>
	</FormField>
</template>

<script setup lang="ts">
defineProps<{
	type: string;
	name: string;
	label: string;
	placeholder: string;
	description?: string;
}>();
</script>
