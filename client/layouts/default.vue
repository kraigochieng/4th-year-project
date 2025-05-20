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

	<div
		class="flex items-center justify-between sticky top-0 z-50 bg-background page-responsive-width py-4"
	>
		<NuxtLink href="/"><Logo /></NuxtLink>

		<NavigationMenu>
			<NavigationMenuList class="flex gap-x-2">
				<NavigationMenuItem>
					<NavigationMenuLink href="/">Home</NavigationMenuLink>
				</NavigationMenuItem>
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
									<NuxtLink to="/adr/add">Add ADR</NuxtLink>
								</NavigationMenuLink>
							</li>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink to="/adr">View ADRs</NuxtLink>
								</NavigationMenuLink>
							</li>
						</ul>
					</NavigationMenuContent>
				</NavigationMenuItem>
				<NavigationMenuItem>
					<NavigationMenuTrigger>Communication</NavigationMenuTrigger>
					<NavigationMenuContent>
						<ul
							class="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]"
						>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink
										to="/communication/additional-info"
									>
										Additional Info
									</NuxtLink>
								</NavigationMenuLink>
							</li>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink to="/communication/bulk-alerts">
										Bulk Alerts
									</NuxtLink>
								</NavigationMenuLink>
							</li>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink
										to="/communication/individual-alerts"
									>
										Individual Alerts
									</NuxtLink>
								</NavigationMenuLink>
							</li>
						</ul>
					</NavigationMenuContent>
				</NavigationMenuItem>
				<NavigationMenuItem>
					<NavigationMenuLink href="/monitoring">
						Monitor
					</NavigationMenuLink>
				</NavigationMenuItem>
				<NavigationMenuItem>
					<Button @mouseup="useAuthStore().logout()">Logout</Button>
				</NavigationMenuItem>
			</NavigationMenuList>
		</NavigationMenu>

		<div>Avatar Here</div>
	</div>

	<slot></slot>
</template>
<script setup lang="ts"></script>

<style scoped>
.glass-bg {
	@apply backdrop-filter backdrop-blur-md bg-opacity-50;
}
</style>
