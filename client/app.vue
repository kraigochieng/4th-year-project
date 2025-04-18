<template>
	<div>
		<NuxtLayout>
			<NuxtPage />
		</NuxtLayout>

		<!-- <NuxtPage /> -->
	</div>
</template>

<style lang="css">
* {
	font-family: "Inter";
}

/* This targets dark mode */
@media (prefers-color-scheme: dark) {
	/* Change the color of the SVG icon to white */
	img[src*="favicon.svg"] {
		filter: invert(100%) brightness(100%);
	}
}

/* This targets light mode */
@media (prefers-color-scheme: light) {
	/* Change the color of the SVG icon to black */
	img[src*="favicon.svg"] {
		filter: invert(0%) brightness(100%);
	}
}

.page-wrapper {
	@apply p-8 lg:px-32;
}

.form-field-wrapper {
	@apply my-8;
}

.page-title {
	@apply text-2xl font-bold mb-6;
}
</style>
