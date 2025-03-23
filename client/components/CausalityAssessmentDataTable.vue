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
// Imports
import { ref, computed, type PropType } from "vue";
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
import {
	TableActionsAdr,
	TableActionsCausalityAssessmentLevel,
} from "#components";

// Types
interface ADRCausality {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	created_at: string;
	updated_at: string;
}
// Props
const props = defineProps({
	data: Array as PropType<ADRCausality[]>,
});
// State
const tableFilter = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const { toast } = useToast();

// Fetch ADR Data
const authStore = useAuthStore();

console.log(props.data);
// Table creation
const tableData = props.data ?? [];

const columns: ColumnDef<ADRCausality>[] = [
	{
		id: "ml_model_id",
		accessorKey: "ml_model_id",
		header: "ML Model ID",
		cell: ({ row }) => h("div", {}, row.getValue("ml_model_id")),
		enableSorting: false,
	},
	{
		id: "causality_assessment_level_value",
		accessorKey: "causality_assessment_level_value",
		header: "Causality Assessment Level",
		cell: ({ row }) =>
			h("div", {}, row.getValue("causality_assessment_level_value")),
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
			return h(TableActionsCausalityAssessmentLevel, {
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
