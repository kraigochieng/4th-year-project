<template>
	<FormField v-slot="{ value }" :name="props.name">
		<div class="form-field-wrapper">
			<FormItem>
				<FormLabel>{{ props.label }}</FormLabel>
				<NumberField
					class="gap-2"
					:min="props.min"
					:model-value="value"
					v-bind="
						props.formatOptions
							? { formatOptions: props.formatOptions }
							: {}
					"
					@update:model-value="
						(v) => {
							if (v) {
								myValue = v;
							} else {
								myValue = undefined;
							}
						}
					"
				>
					<NumberFieldContent>
						<NumberFieldDecrement />
						<FormControl>
							<NumberFieldInput />
						</FormControl>
						<NumberFieldIncrement />
					</NumberFieldContent>
				</NumberField>
				<FormDescription>
					{{ props.description }}
				</FormDescription>
				<FormMessage />
			</FormItem>
		</div>
	</FormField>
</template>

<script setup lang="ts">
const myValue = defineModel<number>();

const props = withDefaults(
	defineProps<{
		name: string;
		label: string;
		description?: string;
		min?: number;
		max?: number;
		formatOptions?: Intl.NumberFormatOptions;
	}>(),
	{
		min: 1,
	}
);
</script>
