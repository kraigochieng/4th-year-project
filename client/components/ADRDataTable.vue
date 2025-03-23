<template>
	<div class="rounded-md border">
		<Table>
			<TableHeader>
				<TableRow
					v-for="headerGroup in table.getHeaderGroups()"
					:key="headerGroup.id"
				>
					<TableHead
						v-for="header in headerGroup.headers"
						:key="header.id"
					>
						<FlexRender
							v-if="!header.isPlaceholder"
							:render="header.column.columnDef.header"
							:props="header.getContext()"
						/>
					</TableHead>
				</TableRow>
			</TableHeader>
			<TableBody>
				<template v-if="table.getRowModel().rows?.length">
					<template
						v-for="row in table.getRowModel().rows"
						:key="row.id"
					>
						<TableRow
							:data-state="row.getIsSelected() && 'selected'"
						>
							<TableCell
								v-for="cell in row.getVisibleCells()"
								:key="cell.id"
							>
								<FlexRender
									:render="cell.column.columnDef.cell"
									:props="cell.getContext()"
								/>
							</TableCell>
						</TableRow>
						<TableRow v-if="row.getIsExpanded()">
							<TableCell :colspan="row.getAllCells().length">
								{{ JSON.stringify(row.original) }}
							</TableCell>
						</TableRow>
					</template>
				</template>

				<TableRow v-else>
					<TableCell
						:colspan="columns.length"
						class="h-24 text-center"
					>
						No results.
					</TableCell>
				</TableRow>
			</TableBody>
		</Table>
	</div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "@/components/ui/toast";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
	Eye,
	Plus,
	Download,
	MoreHorizontal,
	RefreshCcw,
} from "lucide-vue-next";
import {
	getCoreRowModel,
	useVueTable,
	FlexRender,
	type ColumnDef,
} from "@tanstack/vue-table";
import { TableActionsAdr } from "#components";
import Checkbox from "./ui/checkbox/Checkbox.vue";

interface ADRReviewFull {
	id: string;
	patient_id: string;
	user_id: string;
	gender: string;
	pregnancy_status: string;
	known_allergy: string;
	rechallenge: string;
	dechallenge: string;
	severity: string;
	is_serious: string;
	criteria_for_seriousness: string;
	action_taken: string;
	outcome: string;
	created_at: string;
	updated_at: string;
	causality_assessment_levels?: ADRCausality[]; // Array of reviews
}

interface ADRCausality {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	created_at: string;
	updated_at: string;
	reviews: ADRReview[];
}

// Define the ADR & Review interfaces
interface ADRReview {
	id: string;
	causality_assessment_level_id: string;
	user_id: string;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string | null;
	created_at: string;
	updated_at: string;
}

// State
const tableFilter = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const { toast } = useToast();

// Fetch ADR Data
const authStore = useAuthStore();
const {
	data,
	status,
	error,
	refresh: refreshData,
} = useFetch<ADRReviewFull[]>(`${useRuntimeConfig().public.serverApi}/review`, {
	method: "GET",
	headers: {
		Authorization: `Bearer ${authStore.accessToken}`,
	},
});

console.log(data.value);
// Table creation
const tableData = data.value ?? [];

const columns: ColumnDef<ADRReviewFull>[] = [
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
		id: "patient_id",
		accessorKey: "patient_id",
		header: "Patient ID",
		cell: ({ row }) => h("div", {}, row.getValue("patient_id")),
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

const table = useVueTable({
	data: tableData,
	columns: columns,
	getCoreRowModel: getCoreRowModel(),
});
</script>
