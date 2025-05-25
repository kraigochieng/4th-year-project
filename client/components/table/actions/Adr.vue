<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal } from "lucide-vue-next";

const props = defineProps<{
	row: {
		adr_id: string;
	};
}>();

const router = useRouter();

function handleView() {
	router.push(`/adr/${props.row.adr_id}`);
}

function handleEdit() {
	router.push(`/adr/${props.row.adr_id}/edit`);
}
const isOpen = ref(false);
</script>

<template>
	<DropdownMenu>
		<DropdownMenuTrigger as-child>
			<Button variant="ghost" class="w-8 h-8 p-0">
				<span class="sr-only">Open menu</span>
				<MoreHorizontal class="w-4 h-4" />
			</Button>
		</DropdownMenuTrigger>
		<DropdownMenuContent align="end">
			<DropdownMenuLabel>Actions</DropdownMenuLabel>
			<DropdownMenuItem @mouseup="handleView">View ADR</DropdownMenuItem>
			<DropdownMenuItem @mouseup="handleEdit">Edit ADR</DropdownMenuItem>
			<DropdownMenuItem @mouseup="handleEdit">Delete ADR</DropdownMenuItem>
		</DropdownMenuContent>
	</DropdownMenu>
</template>
