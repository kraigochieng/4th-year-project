export function useFeatureNameFormatter(
	featureName: string
): string | undefined {
	if (featureName === "rechallenge_no") return "Rechallenge (No)";
	if (featureName === "rechallenge_na") return "Rechallenge (N/A)";
	if (featureName === "rechallenge_yes") return "Rechallenge (Yes)";
	if (featureName === "rechallenge_unknown") return "Rechallenge (Unknown)";
	if (featureName === "dechallenge_no") return "Dechallenge (No)";
	if (featureName === "dechallenge_na") return "Dechallenge (N/A)";
	if (featureName === "dechallenge_yes") return "Dechallenge (Yes)";
	if (featureName === "dechallenge_unknown") return "Dechallenge (Unknown)";
}
