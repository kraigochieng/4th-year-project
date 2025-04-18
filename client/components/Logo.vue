<template>
	<div class="flex items-center text-primary">
		<Icon
			name="material-symbols-light:settings-heart-outline-rounded"
			size="64px"
		/>
		<p class="text-xl">
			<span class="big-letter">M</span>edi<span class="big-letter">L</span
			>inda
		</p>
	</div>
</template>

<script setup lang="ts"></script>

<style lang="css" scoped>
/* * {
	font-family: "Lexend";
} */

.big-letter {
	@apply font-bold text-2xl;
}
</style>
