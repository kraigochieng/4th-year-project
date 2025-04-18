<script setup lang="ts">
defineProps<{
	name: string;
	label: string;
	description?: string;
	defaultValue?: string;
	options: { value: string; label: string }[];
}>();
</script>

<template>
	<FormField
		v-slot="{ componentField }"
		type="radio"
		:name="name"
		class="form-field-wrapper"
	>
		<FormItem>
			<div class="flex items-center gap-x-1">
				<FormLabel> {{ label }}</FormLabel>
				<HoverCard>
					<HoverCardTrigger>
						<Icon name="ic:twotone-help" />
					</HoverCardTrigger>
					<HoverCardContent>
						{{ description ? description : label }}
					</HoverCardContent>
				</HoverCard>
			</div>

			<FormControl>
				<RadioGroup v-bind="componentField" class="flex gap-4">
					<FormItem
						v-for="option in options"
						class="flex items-center space-y-0 gap-x-1"
					>
						<FormControl>
							<RadioGroupItem :value="option.value" />
						</FormControl>
						<FormLabel>{{ option.label }}</FormLabel>
					</FormItem>
				</RadioGroup>
			</FormControl>
			<FormMessage />
		</FormItem>
	</FormField>
	<!-- <RadioGroup :default-value="defaultValue == undefined ? '' : defaultValue"> -->
</template>
