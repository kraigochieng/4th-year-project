import type { ApexOptions } from "apexcharts";
import { startCase, toLower } from "lodash";

export function usePieChart(title: string, labels: string[], data: number[]) {
	const formattedLabels = labels.map((c) => startCase(toLower(c)));
	return {
		options: {
			chart: {
				type: "pie",
				fontFamily: "Lexend",
				width: 200,
				height: 200,
			},
			labels: formattedLabels,
			title: {
				text: title,
				align: "center",
			},
			responsive: [
				{
					breakpoint: 480,
					options: {
						chart: { width: 200 },
						legend: { position: "bottom" },
					},
				},
			],
		} as ApexOptions,
		series: data as Array<number>,
	};
}

export function useBarChart(
	title: string,
	categories: string[],
	data: number[]
) {
	const formattedCategories = categories.map((c) => startCase(toLower(c)));

	return {
		options: {
			chart: {
				type: "bar",
				fontFamily: "Lexend",
				width: 200,
				height: 200,
			},
			colors: [
				getComputedStyle(document.documentElement).getPropertyValue(
					"--primary"
				),
			],
			xaxis: { categories: formattedCategories },
			title: {
				text: title,
				align: "center",
			},
			plotOptions: {
				bar: { horizontal: true },
			},
		} as ApexOptions,
		series: [{ name: title, data }] as ApexAxisChartSeries,
	};
}
