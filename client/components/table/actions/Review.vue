<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal } from "lucide-vue-next";

const props = defineProps<{
	row: {
		id: string;
	};
}>();

const router = useRouter();

function handleView() {
	router.push(`/review/${props.row.id}`);
}
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
			<DropdownMenuItem @mouseup="handleView">View</DropdownMenuItem>
		</DropdownMenuContent>
	</DropdownMenu>
</template>
