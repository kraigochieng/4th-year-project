<template>
	<FormField :name="props.name">
		<FormItem>
			<FormLabel>{{ props.label }}</FormLabel>
			<Popover>
				<PopoverTrigger as-child>
					<Button
						variant="outline"
						:class="
							cn(
								'w-[280px] justify-start text-left font-normal',
								!value && 'text-muted-foreground'
							)
						"
					>
						<CalendarIcon class="mr-2 h-4 w-4" />
						<template v-if="value.start">
							<template v-if="value.end">
								{{
									df.format(
										value.start.toDate(getLocalTimeZone())
									)
								}}
								-
								{{
									df.format(
										value.end.toDate(getLocalTimeZone())
									)
								}}
							</template>

							<template v-else>
								{{
									df.format(
										value.start.toDate(getLocalTimeZone())
									)
								}}
							</template>
						</template>
						<template v-else> Pick a date </template>
					</Button>
				</PopoverTrigger>
				<PopoverContent class="w-auto p-0">
					<RangeCalendar
						v-model="value"
						initial-focus
						:number-of-months="2"
						@update:start-value="
							(startDate) => (value.start = startDate)
						"
					/>
				</PopoverContent>
			</Popover>
		</FormItem>
	</FormField>
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";
import type { DateRange } from "reka-ui";

import {
	DateFormatter,
	getLocalTimeZone,
	today,
} from "@internationalized/date";
import { CalendarIcon } from "lucide-vue-next";

const df = new DateFormatter("en-US", {
	dateStyle: "medium",
});

// const value = ref({
// 	start: new CalendarDate(2022, 1, 20),
// 	end: new CalendarDate(2022, 1, 20).add({ days: 20 }),
// }) as Ref<DateRange>;
// Helper to get today and 1 month ago
const timezone = getLocalTimeZone();
const end = today(timezone);
const start = end.subtract({ months: 1 });

const value = defineModel<DateRange>({
	default: {
		start: today(getLocalTimeZone()).subtract({ months: 1 }),
		end: today(getLocalTimeZone()),
	},
});
const props = defineProps<{
	name: string;
	label: string;
}>();
</script>
