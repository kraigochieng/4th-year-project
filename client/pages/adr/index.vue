<template>
	<div class="page-wrapper">
		<Button><NuxtLink to="/adr/add">Add Adr</NuxtLink></Button>
		<LoadingMedilinda label="Loading ADRs" v-if="status == 'pending'" />
		<DataTable
			v-if="status == 'success'"
			title="ADR Management"
			:data="data?.items"
			:columns="columns"
			:currentPage="currentPage"
			:pageSize="pageSize"
			:totalCount="totalCount"
			@pageChange="handlePageChange"
			@pageSizeChange="handlePageSizeChange"
		/>

		<div v-if="error" class="mt-4 p-4 rounded bg-red-100 text-red-800">
			<p>{{ error }}</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import TableActionsAdr from "@/components/table/actions/Adr.vue";
import { useAuthStore } from "@/stores/auth";

import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import type { ADRGetResponseInterface } from "@/types/adr";
import type { PaginatedResponseInterface } from "@/types/pagination";
import { type ColumnDef } from "@tanstack/vue-table";

// Fetch ADR Data
const authStore = useAuthStore();

// Create reactive variables for data, status, and error
const data = ref<PaginatedResponseInterface<ADRGetResponseInterface> | null>(
	null
);
const status = ref<"pending" | "success" | "error">("pending");
const error = ref<string | null>(null);

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(() => data.value?.total || 0);

// Fetch data when component is mounted
onMounted(async () => {
	await fetchADRData();
});

const fetchADRData = async () => {
	try {
		status.value = "pending";
		// Using $fetch for API call
		data.value = await $fetch(
			`${useRuntimeConfig().public.serverApi}/adr`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: currentPage.value,
					size: pageSize.value,
				},
			}
		);

		status.value = "success";
	} catch (err: any) {
		status.value = "error";
		error.value = err.message || "Something went wrong";
	}
};

watch([currentPage, pageSize], () => {
	fetchADRData();
});

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};

const columns: ColumnDef<ADRGetResponseInterface>[] = [
	{
		id: "select",
		header: ({ table }) =>
			h(Checkbox, {
				modelValue:
					table.getIsAllPageRowsSelected() ||
					(table.getIsSomePageRowsSelected() && "indeterminate"),
				"onUpdate:modelValue": (value) =>
					table.toggleAllPageRowsSelected(!!value),
				ariaLabel: "Select all",
			}),
		cell: ({ row }) =>
			h(Checkbox, {
				modelValue: row.getIsSelected(),
				"onUpdate:modelValue": (value) => row.toggleSelected(!!value),
				ariaLabel: "Select row",
			}),
		enableSorting: false,
		enableHiding: false,
	},
	{
		id: "patient_name",
		accessorKey: "patient_name",
		header: "Patient Name",
		cell: ({ row }) => h("div", {}, row.getValue("patient_name")),
		enableSorting: false,
	},
	{
		id: "gender",
		accessorKey: "gender",
		header: "Gender",
		cell: ({ row }) => h("div", {}, row.getValue("gender")),
	},
	// {
	// 	accessorKey:
	// 		"causality_assessment_levels.causality_assessment_level_value",
	// 	header: "Causality Assessment Level",
	// 	cell: ({ row }) =>
	// 		h(
	// 			"div",
	// 			{},
	// 			row.getValue(
	// 				"causality_assessment_levels"
	// 			)
	// 		),
	// },
	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsAdr, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];

useHead({ title: "ADR | MediLinda" });
</script>
