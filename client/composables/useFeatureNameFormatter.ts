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
	if (featureName === "severity_fatal") return "Severity (Fatal)";
	if (featureName === "num_suspected_drugs_1") return "No. of Suspected Drugs (1)";
	if (featureName === "patient_weight_kg") return "Patient Weight (kg)";
	if (featureName === "patient_height_cm") return "Patient Height (cm)";
	return featureName
}
