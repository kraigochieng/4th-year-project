<template>
	<div class="page-wrapper">
		<p class="page-title">Dashboard</p>
		<Tabs default-value="overview">
			<TabsList>
				<TabsTrigger value="overview">Overview</TabsTrigger>
				<TabsTrigger value="adr">Adverse Drug Reaction</TabsTrigger>
				<TabsTrigger value="sms">SMS</TabsTrigger>
			</TabsList>
			<TabsContent value="overview">
				<div class="flex gap-4 my-8">
					<Card v-for="card in summaryCards" :key="card.label">
						<CardHeader>
							<div
								class="flex justify-between items-center gap-2"
							>
								<p class="text-sm text-muted-foreground">
									{{ card.label }}
								</p>
								<Icon
									:name="card.icon"
									class="w-6 h-6 text-gray-400"
								/>
							</div>
						</CardHeader>
						<CardContent>
							<p class="text-xl font-bold">{{ card.value }}</p>
						</CardContent>
					</Card>
				</div>
				<div class="chart-group-wrapper">
					<ApexChart
						v-if="causalityDistributionChart"
						:options="causalityDistributionChart.options"
						:series="causalityDistributionChart.series"
					/>
					<ApexChart
						v-if="reviewedUnreviewedChart"
						:options="reviewedUnreviewedChart.options"
						:series="reviewedUnreviewedChart.series"
					/>
					<ApexChart
						v-if="approvalStatusChart"
						:options="approvalStatusChart.options"
						:series="approvalStatusChart.series"
					/>
					<ApexChart
						v-if="topInstitutionsChart"
						:options="topInstitutionsChart.options"
						:series="topInstitutionsChart.series"
					/>
					<!-- <ApexChart
						v-if="adrWeeklyChart"
						:options="adrWeeklyChart.options"
						:series="adrWeeklyChart.series"
					/> -->
					<div class="flex">
						<Select
							v-model="selectedYear"
							placeholder="Select year"
							class="w-48"
						>
							<SelectTrigger>
								<SelectValue placeholder="Select year" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem
									v-for="year in availableYears"
									:key="year"
									:value="year"
								>
									{{ year }}
								</SelectItem>
							</SelectContent>
						</Select>
						<ApexChart
							v-if="
								selectedYear &&
								adrMonthlyByYearChart &&
								adrMonthlyByYearChart[selectedYear]
							"
							:options="
								useLineChart(
									`ADRs Reported Monthly - ${selectedYear}`,
									adrMonthlyByYearChart[selectedYear].data,
									adrMonthlyByYearChart[selectedYear].series
								).options
							"
							:series="
								useLineChart(
									`ADRs Reported Monthly - ${selectedYear}`,
									adrMonthlyByYearChart[selectedYear].data,
									adrMonthlyByYearChart[selectedYear].series
								).series
							"
						/>
					</div>
				</div>
			</TabsContent>
			<TabsContent value="adr">
				<div class="chart-group-wrapper">
					<ApexChart
						v-for="(chart, index) in adrCategoricalCharts"
						:key="index"
						:options="chart.options"
						:series="chart.series"
					/>
				</div>
			</TabsContent>
			<TabsContent value="sms"></TabsContent>
		</Tabs>
	</div>
</template>

<script setup>
const authStore = useAuthStore();
const serverApi = useRuntimeConfig().public.serverApi;
const headers = { Authorization: `Bearer ${authStore.accessToken}` };

const summaryCards = ref([]);
const reviewedUnreviewedChart = ref(null);
const causalityDistributionChart = ref(null);
const approvalStatusChart = ref(null);
const topInstitutionsChart = ref(null);
const adrWeeklyChart = ref(null);
const adrMonthlyByYearChart = ref(null);

const selectedYear = ref(null);
const availableYears = ref([]);

// Fetch categorical field data and generate charts
// For ADR categorical field charts
const adrCategoricalCharts = ref([]);

// List your categorical fields here exactly as named in the ADRModel
const adrCategoricalFields = [
	"patient_gender",
	"known_allergy",
	"pregnancy_status",
	"rechallenge",
	"dechallenge",
	"severity",
	"is_serious",
	"criteria_for_seriousness",
	"action_taken",
	"outcome",
];

function cleanEnumLabel(label) {
	if (!label) return "";
	// Remove everything before last dot (.) if present
	const parts = label.split(".");
	return parts.length > 1 ? parts[parts.length - 1] : label;
}

onMounted(async () => {
	// const [
	// 	summary,
	// 	reviewedUnreviewed,
	// 	causalityDistribution,
	// 	approvalStatus,
	// 	topInstitutions,
	// 	adrWeekly,
	// 	adrMonthlyByYear,
	// ] = await Promise.all([
	// 	$fetch(`${serverApi}/dashboard/summary`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/reviewed-unreviewed`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/causality-distribution`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/approval-status`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/top-institutions`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/adrs-weekly`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/adrs-monthly`, { headers }),
	// ]);
	const summary = await $fetch(`${serverApi}/dashboard/summary`, { headers });

	const reviewedUnreviewed = await $fetch(
		`${serverApi}/dashboard/reviewed-unreviewed`,
		{ headers }
	);

	const causalityDistribution = await $fetch(
		`${serverApi}/dashboard/causality-distribution`,
		{ headers }
	);

	const approvalStatus = await $fetch(
		`${serverApi}/dashboard/approval-status`,
		{ headers }
	);

	const topInstitutions = await $fetch(
		`${serverApi}/dashboard/top-institutions`,
		{ headers }
	);

	const adrWeekly = await $fetch(`${serverApi}/dashboard/adrs-weekly`, {
		headers,
	});

	const adrMonthlyByYear = await $fetch(
		`${serverApi}/dashboard/adrs-monthly`,
		{ headers }
	);

	if (adrMonthlyByYear.value) {
		availableYears.value = Object.keys(adrMonthlyByYear.value);
		selectedYear.value = availableYears.value[0]; // default to first year
	}

	summaryCards.value = [
		{
			label: "Total ADR Reports",
			value: summary.value?.total_adrs,
			icon: "lucide:file-question",
		},
		{
			label: "Total Medical Institutions",
			value: summary.value?.total_institutions,
			icon: "lucide:hospital",
		},
	];

	reviewedUnreviewedChart.value = reviewedUnreviewed.value
		? useBarChart(
				"Reviewed ADRs vs Unreviewed ADRs",
				reviewedUnreviewed.value.data,
				reviewedUnreviewed.value.series
		  )
		: null;

	let cleanedCausalityLabels = [];
	if (causalityDistribution.value) {
		cleanedCausalityLabels =
			causalityDistribution.value.data.map(cleanEnumLabel);
	}

	causalityDistributionChart.value = causalityDistribution.value
		? useBarChart(
				"Causality Assessment Distribution",
				cleanedCausalityLabels,
				causalityDistribution.value.series
		  )
		: null;
	approvalStatusChart.value = approvalStatus.value
		? useBarChart(
				"Approved ADRs VS Unapproved ADRs",
				approvalStatus.value.data,
				approvalStatus.value.series
		  )
		: null;
	topInstitutionsChart.value = topInstitutions.value
		? useBarChart(
				"Top Reporting Institutions",
				topInstitutions.value.data,
				topInstitutions.value.series
		  )
		: null;
	adrWeeklyChart.value = adrWeekly.value
		? useBarChart(
				"ADRs Reported Weekly",
				adrWeekly.value.data,
				adrWeekly.value.series
		  )
		: null;

	adrMonthlyByYearChart.value = adrMonthlyByYear.value;

	adrCategoricalCharts.value = [];

	for (const field of adrCategoricalFields) {
		const { data } = await useFetch(
			`${serverApi}/dashboard/categorical-field/${field}`,
			{ headers }
		);
		if (data.value) {
			// Clean labels
			const cleanedLabels = data.value.data.map(cleanEnumLabel);
			adrCategoricalCharts.value.push(
				useBarChart(
					field
						.replace(/_/g, " ")
						.replace(/\b\w/g, (c) => c.toUpperCase()),
					cleanedLabels,
					data.value.series
				)
			);
		}
	}
});

useHead({ title: "Dashboard | MediLinda" });
</script>

<style scoped>
.grid-cols-2 > * {
	min-width: 0;
}

.chart-group-wrapper {
	@apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}
</style>
