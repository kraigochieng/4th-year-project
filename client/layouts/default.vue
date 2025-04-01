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
		class="flex items-center justify-between sticky top-0 z-50 bg-white border-b"
	>
		<NuxtLink href="/" class="flex items-center"
			><Icon
				name="material-symbols-light:settings-heart-outline-rounded"
				size="64px"
			/>
			<p>MediLinda</p></NuxtLink
		>

		<NavigationMenu>
			<NavigationMenuList>
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
					<Button @click="useAuthStore().logout()">Logout</Button>
				</NavigationMenuItem>
			</NavigationMenuList>
		</NavigationMenu>
		<div>Avatar Here</div>
	</div>

	<slot></slot>
</template>
<script setup lang="ts"></script>
