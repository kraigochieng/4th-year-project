<template>
	<div v-if="status == 'success'">
		<div class="flex flex-wrap">
			<div class="chart-wrapper">
			<ApexChart
				:options="genderProportionsChart?.options"
				:series="genderProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="pregnancyStatusProportionsChart?.options"
				:series="pregnancyStatusProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="knownChallengeProportionsChart?.options"
				:series="knownChallengeProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="dechallengeProportionsChart?.options"
				:series="dechallengeProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="rechallengeProportionsChart?.options"
				:series="rechallengeProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="severityProportionsChart?.options"
				:series="severityProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="criteriaForSeriousnessProportionsChart?.options"
				:series="criteriaForSeriousnessProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="isSeriousProportionsChart?.options"
				:series="isSeriousProportionsChart?.series"
			></ApexChart>
		</div>
		<div class="chart-wrapper">
			<ApexChart
				:options="outcomeProportionsChart?.options"
				:series="outcomeProportionsChart?.series"
			></ApexChart>
		</div>
		</div>
		
	</div>
	<p v-else="status == 'error'">{{ error }}</p>
</template>

<script setup lang="ts">
import type { ApexOptions } from "apexcharts";

// Interfaces
interface Proportions {
	series: string[];
	data: number[];
}

interface MonitoringData {
	gender_proportions: Proportions;
	pregnancy_status_proportions: Proportions;
	known_allergy_proportions: Proportions;
	dechallenge_proportions: Proportions;
	rechallenge_proportions: Proportions;
	severity_proportions: Proportions;
	criteria_for_seriousness_proportions: Proportions;
	is_serious_proportions: Proportions;
	outcome_proportions: Proportions;
}
// State
const data = ref<MonitoringData | null>(null);
const status = ref<"pending" | "success" | "error">("pending");
const error = ref<string | null>(null);

// Stores
const authStore = useAuthStore();

// Lifecycle Hooks
onMounted(async () => {
	await fetchMonitoringData();
});

const fetchMonitoringData = async () => {
	try {
		status.value = "pending";
		// Using $fetch for API call
		data.value = await $fetch(
			`${useRuntimeConfig().public.serverApi}/monitoring`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);
		status.value = "success";
	} catch (err: any) {
		status.value = "error";
		error.value = err.message || "Something went wrong";
	}
};

// Graphs

interface BarChart {
	options: ApexOptions;
	series: ApexAxisChartSeries;
}

interface PieChart {
	options: ApexOptions;
	series: Array<number>;
}

// Charts
const genderProportionsChart = ref<PieChart | null>(null);
const pregnancyStatusProportionsChart = ref<BarChart | null>(null);
const knownChallengeProportionsChart = ref<BarChart | null>(null);
const dechallengeProportionsChart = ref<BarChart | null>(null);
const rechallengeProportionsChart = ref<BarChart | null>(null);
const severityProportionsChart = ref<BarChart | null>(null);
const criteriaForSeriousnessProportionsChart = ref<BarChart | null>(null);
const isSeriousProportionsChart = ref<PieChart | null>(null);
const outcomeProportionsChart = ref<BarChart | null>(null);

watchEffect(() => {
	if (!data.value) return;
	genderProportionsChart.value = usePieChart(
		"Gender Proportions",
		data.value.gender_proportions.series,
		data.value.gender_proportions.data
	);

	pregnancyStatusProportionsChart.value = useBarChart(
		"Pregnancy Status Proportions",
		data.value.pregnancy_status_proportions.series,
		data.value.pregnancy_status_proportions.data
	);

	knownChallengeProportionsChart.value = useBarChart(
		"Known Allergy Proportions",
		data.value.known_allergy_proportions.series,
		data.value.known_allergy_proportions.data
	);

	dechallengeProportionsChart.value = useBarChart(
		"Dechallenge Proportions",
		data.value.dechallenge_proportions.series,
		data.value.dechallenge_proportions.data
	);

	rechallengeProportionsChart.value = useBarChart(
		"Rechallenge Proportions",
		data.value.rechallenge_proportions.series,
		data.value.rechallenge_proportions.data
	);

	severityProportionsChart.value = useBarChart(
		"Severity Proportions",
		data.value.severity_proportions.series,
		data.value.severity_proportions.data
	);

	criteriaForSeriousnessProportionsChart.value = useBarChart(
		"Criteria For Seriousness Proportions",
		data.value.criteria_for_seriousness_proportions.series,
		data.value.criteria_for_seriousness_proportions.data
	);

	isSeriousProportionsChart.value = usePieChart(
		"Is Serious Proportions",
		data.value.is_serious_proportions.series,
		data.value.is_serious_proportions.data
	);

	outcomeProportionsChart.value = useBarChart(
		"Outcome Proportions",
		data.value.outcome_proportions.series,
		data.value.outcome_proportions.data
	);
});
</script>

<style scoped>
.chart-wrapper {
	width: 100%;
	max-width: 600px;
	/* height: 400px; */
}
</style>
