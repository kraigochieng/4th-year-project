<template>
	<!-- <SidebarProvider>
		<Sidebar>
			<SidebarContent>
				<SidebarGroup>Home</SidebarGroup>
				<SidebarMenu>
					<SidebarMenuItem>
						<SidebarMenuButton
							><NuxtLink to="/">Test</NuxtLink></SidebarMenuButton
						>
					</SidebarMenuItem>
					<SidebarMenuItem>
						<SidebarMenuButton
							><NuxtLink to="/about"
								>About</NuxtLink
							></SidebarMenuButton
						>
					</SidebarMenuItem>
				</SidebarMenu>
			</SidebarContent>
		</Sidebar>
		<div>
			<SidebarTrigger />
			<slot></slot>
		</div>
	</SidebarProvider> -->

	<NavigationMenu>
		<NavigationMenuList>
			<NavigationMenuItem>
				<NavigationMenuTrigger>ADR</NavigationMenuTrigger>
				<NavigationMenuContent>
					<ul
						class="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]"
					>
						<li>
							<NavigationMenuLink
								as-child
								class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
							>
								<NuxtLink to="/adr"
									>Go to ADR Home page</NuxtLink
								>
							</NavigationMenuLink>
						</li>
						<li>
							<NavigationMenuLink
								as-child
								class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
							>
								<NuxtLink to="/adr/add"> Add ADR</NuxtLink>
							</NavigationMenuLink>
						</li>
						<li>
							<NavigationMenuLink
								as-child
								class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
							>
								<NuxtLink to="/adr/review">Review</NuxtLink>
							</NavigationMenuLink>
						</li>
						<li>
							<Button @click="useAuthStore().logout()">Logout</Button>
						</li>
					</ul>
				</NavigationMenuContent>
			</NavigationMenuItem>
		</NavigationMenuList>
	</NavigationMenu>

	<slot></slot>
</template>
<script setup lang="ts">
import { navigationMenuTriggerStyle } from "@/components/ui/navigation-menu";
import NavigationMenu from "~/components/ui/navigation-menu/NavigationMenu.vue";
import NavigationMenuItem from "~/components/ui/navigation-menu/NavigationMenuItem.vue";
import NavigationMenuLink from "~/components/ui/navigation-menu/NavigationMenuLink.vue";
import NavigationMenuList from "~/components/ui/navigation-menu/NavigationMenuList.vue";
import NavigationMenuTrigger from "~/components/ui/navigation-menu/NavigationMenuTrigger.vue";
import NavigationMenuContent from "~/components/ui/navigation-menu/NavigationMenuContent.vue";
import Sidebar from "~/components/ui/sidebar/Sidebar.vue";
import SidebarContent from "~/components/ui/sidebar/SidebarContent.vue";
import SidebarMenuButton from "~/components/ui/sidebar/SidebarMenuButton.vue";
import SidebarMenuItem from "~/components/ui/sidebar/SidebarMenuItem.vue";
import SidebarProvider from "~/components/ui/sidebar/SidebarProvider.vue";
import SidebarTrigger from "~/components/ui/sidebar/SidebarTrigger.vue";
</script>
