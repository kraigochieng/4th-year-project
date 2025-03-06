<template>
	<div class="w-full">
		<div class="flex items-center py-4 justify-between">
			<Input
				v-model="tableFilter"
				placeholder="Filter ADRs..."
				class="max-w-sm"
			/>
			<Button @click="refreshData" size="sm">
				<RefreshCcw class="h-4 w-4 mr-2" />
				Refresh
			</Button>
		</div>

		<div class="rounded-md border">
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead>Patient ID</TableHead>
						<TableHead>Gender</TableHead>
						<TableHead>Severity</TableHead>
						<TableHead>Is Serious</TableHead>
						<TableHead>Causality Level</TableHead>
						<TableHead>Created At</TableHead>
						<TableHead>Reviews</TableHead>
						<TableHead>Actions</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					<TableRow v-if="status === 'pending'">
						<TableCell colspan="8" class="text-center py-10">
							<div class="flex justify-center items-center">
								<div
									class="animate-spin h-5 w-5 mr-2 border-2 border-primary border-t-transparent rounded-full"
								></div>
								Loading data...
							</div>
						</TableCell>
					</TableRow>
					<TableRow v-else-if="status === 'error'">
						<TableCell
							colspan="8"
							class="text-center py-10 text-red-500"
						>
							Error loading data: {{ error }}
						</TableCell>
					</TableRow>
					<TableRow v-else-if="filteredData.length === 0">
						<TableCell colspan="8" class="text-center py-10">
							No ADR reviews found.
						</TableCell>
					</TableRow>
					<TableRow
						v-for="adr in filteredData"
						:key="adr.id"
						class="hover:bg-muted/50"
					>
						<TableCell>{{ adr.patient_id }}</TableCell>
						<TableCell>{{ adr.gender }}</TableCell>
						<TableCell>
							<Badge :variant="getSeverityVariant(adr.severity)">
								{{ adr.severity }}
							</Badge>
						</TableCell>
						<TableCell>
							<Badge
								:variant="
									adr.is_serious === 'Yes'
										? 'destructive'
										: 'outline'
								"
							>
								{{ adr.is_serious }}
							</Badge>
						</TableCell>
						<TableCell>{{
							adr.causality_assessment_level
						}}</TableCell>
						<TableCell>{{ formatDate(adr.created_at) }}</TableCell>
						<TableCell>
							<Badge variant="secondary">
								{{ adr.reviews?.length || 0 }} reviews
							</Badge>
						</TableCell>
						<TableCell>
							<DropdownMenu>
								<DropdownMenuTrigger asChild>
									<Button variant="ghost" class="h-8 w-8 p-0">
										<MoreHorizontal class="h-4 w-4" />
										<span class="sr-only">Open menu</span>
									</Button>
								</DropdownMenuTrigger>
								<DropdownMenuContent align="end">
									<DropdownMenuLabel
										>Actions</DropdownMenuLabel
									>
									<DropdownMenuItem @click="viewADR(adr)">
										<Eye class="h-4 w-4 mr-2" />
										View Details
									</DropdownMenuItem>
									<DropdownMenuItem @click="addReview(adr)">
										<Plus class="h-4 w-4 mr-2" />
										Add Review
									</DropdownMenuItem>
									<DropdownMenuSeparator />
									<DropdownMenuItem @click="exportADR(adr)">
										<Download class="h-4 w-4 mr-2" />
										Export
									</DropdownMenuItem>
								</DropdownMenuContent>
							</DropdownMenu>
						</TableCell>
					</TableRow>
				</TableBody>
			</Table>
		</div>

		<div class="flex items-center justify-between space-x-2 py-4">
			<div class="text-sm text-muted-foreground">
				Showing
				<span class="font-medium">{{ filteredData.length }}</span> of
				<span class="font-medium">{{ data?.length || 0 }}</span> ADRs
			</div>
			<div class="flex space-x-2">
				<Button
					variant="outline"
					size="sm"
					:disabled="currentPage === 1"
					@click="currentPage--"
				>
					Previous
				</Button>
				<Button
					variant="outline"
					size="sm"
					:disabled="currentPage * pageSize >= (data?.length || 0)"
					@click="currentPage++"
				>
					Next
				</Button>
			</div>
		</div>
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

// Define the ADR & Review interfaces
interface ADRReview {
	id: string;
	adr_id: string;
	user_id: string;
	approved: boolean;
	proposed_causality_level?: string | null;
	reason?: string | null;
	created_at: string;
	updated_at: string;
}

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
	causality_assessment_level: string;
	created_at: string;
	updated_at: string;
	reviews?: ADRReview[]; // Array of reviews
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
} = useFetch<ADRReviewFull[]>(
	`${useRuntimeConfig().public.serverApi}/adr/review`,
	{
		method: "GET",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	}
);

// Computed properties
const filteredData = computed(() => {
	if (!data.value) return [];

	let filtered = [...data.value];

	// Apply filter if any
	if (tableFilter.value) {
		const searchTerm = tableFilter.value.toLowerCase();
		filtered = filtered.filter(
			(adr) =>
				adr.patient_id.toLowerCase().includes(searchTerm) ||
				adr.gender.toLowerCase().includes(searchTerm) ||
				adr.severity.toLowerCase().includes(searchTerm) ||
				adr.causality_assessment_level
					.toLowerCase()
					.includes(searchTerm)
		);
	}

	// Apply pagination
	const start = (currentPage.value - 1) * pageSize.value;
	const end = start + pageSize.value;

	return filtered.slice(start, end);
});

// Helper functions
function formatDate(dateString: string): string {
	return new Date(dateString).toLocaleDateString("en-US", {
		year: "numeric",
		month: "short",
		day: "numeric",
	});
}

function getSeverityVariant(severity: string): string {
	switch (severity.toLowerCase()) {
		case "mild":
			return "secondary";
		case "moderate":
			return "warning";
		case "severe":
			return "destructive";
		default:
			return "outline";
	}
}

// Action handlers
function viewADR(adr: ADRReviewFull) {
	// Navigate to detail page or open modal
	console.log("View ADR:", adr.id);
	// navigateTo(`/adr/${adr.id}`)
}

function addReview(adr: ADRReviewFull) {
	// Open review form modal
	console.log("Add review for ADR:", adr.id);
}

function exportADR(adr: ADRReviewFull) {
	// Export ADR data to CSV or PDF
	console.log("Export ADR:", adr.id);
	toast({
		title: "Export Started",
		description: `Exporting data for patient ${adr.patient_id}`,
	});
}
</script>





<!-- <template>
    <div class="w-full">
      <div class="flex items-center py-4 justify-between">
        <Input
          v-model="tableFilter"
          placeholder="Filter ADRs..."
          class="max-w-sm"
          @keyup.enter="fetchData"
        />
        <Button @click="fetchData" size="sm">
          <RefreshCcw class="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>
  
      <div class="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Patient ID</TableHead>
              <TableHead>Gender</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Is Serious</TableHead>
              <TableHead>Causality Level</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Reviews</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-if="loading">
              <TableCell colspan="8" class="text-center py-10">
                <div class="flex justify-center items-center">
                  <div class="animate-spin h-5 w-5 mr-2 border-2 border-primary border-t-transparent rounded-full"></div>
                  Loading data...
                </div>
              </TableCell>
            </TableRow>
            <TableRow v-else-if="error">
              <TableCell colspan="8" class="text-center py-10 text-red-500">
                Error loading data: {{ error }}
              </TableCell>
            </TableRow>
            <TableRow v-else-if="adrs.length === 0">
              <TableCell colspan="8" class="text-center py-10">
                No ADR reviews found.
              </TableCell>
            </TableRow>
            <TableRow v-for="adr in adrs" :key="adr.id" class="hover:bg-muted/50">
              <TableCell>{{ adr.patient_id }}</TableCell>
              <TableCell>{{ adr.gender }}</TableCell>
              <TableCell>
                <Badge :variant="getSeverityVariant(adr.severity)">
                  {{ adr.severity }}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge :variant="adr.is_serious === 'Yes' ? 'destructive' : 'outline'">
                  {{ adr.is_serious }}
                </Badge>
              </TableCell>
              <TableCell>{{ adr.causality_assessment_level }}</TableCell>
              <TableCell>{{ formatDate(adr.created_at) }}</TableCell>
              <TableCell>
                <Badge variant="secondary">
                  {{ adr.reviews?.length || 0 }} reviews
                </Badge>
              </TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" class="h-8 w-8 p-0">
                      <MoreHorizontal class="h-4 w-4" />
                      <span class="sr-only">Open menu</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                    <DropdownMenuItem @click="viewADR(adr)">
                      <Eye class="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem @click="addReview(adr)">
                      <Plus class="h-4 w-4 mr-2" />
                      Add Review
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem @click="exportADR(adr)">
                      <Download class="h-4 w-4 mr-2" />
                      Export
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
  
      <div class="flex items-center justify-between space-x-2 py-4">
        <div class="text-sm text-muted-foreground">
          Showing <span class="font-medium">{{ adrs.length }}</span> items
          <span v-if="totalItems" class="font-medium">of {{ totalItems }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <Select v-model="pageSize" @update:modelValue="onPageSizeChange">
            <option value="10">10 per page</option>
            <option value="20">20 per page</option>
            <option value="50">50 per page</option>
            <option value="100">100 per page</option>
          </Select>
          <div class="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              :disabled="currentPage === 1"
              @click="previousPage"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              :disabled="!hasMorePages"
              @click="nextPage"
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import { useToast } from '@/components/ui/toast'
  import { 
    Table, 
    TableBody, 
    TableCell, 
    TableHead, 
    TableHeader, 
    TableRow 
  } from '@/components/ui/table'
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
  } from '@/components/ui/dropdown-menu'
  import { Button } from '@/components/ui/button'
  import { Input } from '@/components/ui/input'
  import { Badge } from '@/components/ui/badge'
  import { Select } from '@/components/ui/select'
  import { Eye, Plus, Download, MoreHorizontal, RefreshCcw } from 'lucide-vue-next'
  
  // Define the ADR & Review interfaces
  interface ADRReview {
    id: string;
    adr_id: string;
    user_id: string;
    approved: boolean;
    proposed_causality_level?: string | null;
    reason?: string | null;
    created_at: string;
    updated_at: string;
  }
  
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
    causality_assessment_level: string;
    created_at: string;
    updated_at: string;
    reviews?: ADRReview[]; // Array of reviews
  }
  
  interface ApiResponse {
    data: ADRReviewFull[];
    meta?: {
      total: number;
      skip: number;
      limit: number;
    };
  }
  
  // State
  const authStore = useAuthStore()
  const { toast } = useToast()
  const adrs = ref<ADRReviewFull[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalItems = ref<number | null>(null)
  const currentPage = ref(1)
  const pageSize = ref<number>(10)
  const tableFilter = ref('')
  const hasMorePages = ref(true)
  
  // Computed values - Setting default skip to 0 as requested
  const skip = computed(() => {
    if (currentPage.value === 1) {
      return 0; // Default skip for first page is 0
    }
    return (currentPage.value - 1) * pageSize.value;
  })
  
  // Fetch data with pagination
  async function fetchData() {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = new URLSearchParams({
        skip: skip.value.toString(),
        limit: pageSize.value.toString()
      })
      
      // Add search filter if provided
      if (tableFilter.value) {
        queryParams.append('search', tableFilter.value)
      }
      
      const response = await fetch(
        `${useRuntimeConfig().public.serverApi}/adr/review?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${authStore.accessToken}`,
          },
        }
      )
      
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`)
      }
      
      const result: ApiResponse = await response.json()
      adrs.value = result.data
      
      // Update total and check if we have more pages
      if (result.meta) {
        totalItems.value = result.meta.total
        hasMorePages.value = (result.meta.skip + result.meta.limit) < result.meta.total
      } else {
        // If the API doesn't return total items, we'll determine if we have more pages
        // based on whether we got a full page of results
        hasMorePages.value = adrs.value.length === pageSize.value
      }
      
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error occurred'
      console.error('Error fetching ADR data:', err)
    } finally {
      loading.value = false
    }
  }
  
  // Pagination functions
  function nextPage() {
    currentPage.value++
    fetchData()
  }
  
  function previousPage() {
    if (currentPage.value > 1) {
      currentPage.value--
      fetchData()
    }
  }
  
  function onPageSizeChange() {
    // Reset to first page when changing page size
    currentPage.value = 1
    fetchData()
  }
  
  // Helper functions
  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
  
  function getSeverityVariant(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'mild':
        return 'secondary'
      case 'moderate':
        return 'warning'
      case 'severe':
        return 'destructive'
      default:
        return 'outline'
    }
  }
  
  // Action handlers
  function viewADR(adr: ADRReviewFull) {
    console.log('View ADR:', adr.id)
    // navigateTo(`/adr/${adr.id}`)
  }
  
  function addReview(adr: ADRReviewFull) {
    console.log('Add review for ADR:', adr.id)
  }
  
  function exportADR(adr: ADRReviewFull) {
    console.log('Export ADR:', adr.id)
    toast({
      title: 'Export Started',
      description: `Exporting data for patient ${adr.patient_id}`,
    })
  }
  
  // Initialize with default values (0 skip, 10 limit)
  onMounted(() => {
    // Set initial pageSize to 10 (limit)
    pageSize.value = 10;
    
    // Set initial page to 1 (which will result in skip=0)
    currentPage.value = 1;
    
    // Fetch data with these defaults
    fetchData();
  })
  </script> -->