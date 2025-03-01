import { X } from "lucide-vue-next";
import * as z from "zod";

export const adrFormValidationSchema = z.object({
	// patientName: z.string(),
	// dateOfBirth: z.string(),
	patientId: z.string().default("a3ae9b3c-19e2-44a7-b992-5f9f7d341e40"),
	gender: z
		.enum(
			adrFormCategoricalValues["gender"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("male"),
	pregnancyStatus: z
		.enum(
			adrFormCategoricalValues["pregnancyStatus"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("not applicable"),
	knownAllergy: z
		.enum(
			adrFormCategoricalValues["knownAllergy"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("no"),
	rechallenge: z
		.enum(
			adrFormCategoricalValues["rechallenge"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("yes"),
	dechallenge: z
		.enum(
			adrFormCategoricalValues["dechallenge"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("yes"),
	severity: z
		.enum(
			adrFormCategoricalValues["severity"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("mild"),
	isSerious: z
		.enum(
			adrFormCategoricalValues["isSerious"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("no"),
	criteriaForSeriousness: z
		.enum(
			adrFormCategoricalValues["criteriaForSeriousness"].map(
				(x) => x.value
			) as [string, ...string[]]
		)
		.default("hospitalisation"),
	actionTaken: z
		.enum(
			adrFormCategoricalValues["actionTaken"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("unknown"),
	outcome: z
		.enum(
			adrFormCategoricalValues["outcome"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("recovered"),
});

export type adrFormTypeValidationSchema = z.infer<typeof adrFormValidationSchema>;