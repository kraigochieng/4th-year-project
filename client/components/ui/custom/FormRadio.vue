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
	<FormField v-slot="{ componentField }" type="radio" :name="name">
		<FormItem>
			<FormLabel> {{ label }}</FormLabel>
			<HoverCard>
				<HoverCardTrigger>
					<Icon name="ic:twotone-help" />
				</HoverCardTrigger>
				<HoverCardContent>
					{{ description ? description : label }}
				</HoverCardContent>
			</HoverCard>

			<FormControl>
				<RadioGroup
					v-bind="componentField"
					class="flex flex-col space-y-1"
				>
					<FormItem
						v-for="option in options"
						class="flex items-center space-y-0 gap-x-3"
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
