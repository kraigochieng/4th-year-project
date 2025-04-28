<template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>Predicted Causality Level</CardTitle>
			<CardDescription
				>Predicted level is the visible one</CardDescription
			>
		</CardHeader>
		<CardContent>
			<div class="flex md:flex-col w-max mx-auto">
				<div
					v-for="(level, i) in levels"
					:key="i"
					class="box-size"
					:class="[
						level.color,
						props.value === level.label.toLocaleLowerCase()
							? 'opacity-100 shadow-2xl scale-110 z-10'
							: 'opacity-30',
						level.textColor ?? 'text-black',
						level.border ?? 'border-none',
					]"
				>
					{{ level.label }}
				</div>
			</div>
		</CardContent>
	</Card>
</template>

<script setup lang="ts">
import type { CausalityAssessmentLevelEnum } from "@/types/adr";

import { capitalize } from "lodash";
const props = defineProps<{
	value?: CausalityAssessmentLevelEnum;
}>();

const levels = [
	{ label: "Unclassifiable", color: "bg-slate-300", border: "rounded-l-sm" },
	{ label: "Unclassified", color: "bg-slate-500", textColor: "text-white" },
	{ label: "Unlikely", color: "bg-yellow-300" },
	{ label: "Possible", color: "bg-yellow-500" },
	{ label: "Likely", color: "bg-red-300" },
	{
		label: "Certain",
		color: "bg-red-500",
		textColor: "text-white",
		border: "rounded-r-sm",
	},
];
</script>

<style scoped>
.box-size {
	@apply p-1 lg:w-[256px] w-[128px] text-center transition-transform duration-300 transform;
}
</style>
