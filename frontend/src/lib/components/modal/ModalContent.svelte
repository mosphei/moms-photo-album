<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		children,
		contentRef = $bindable()
	}: {
		children: Snippet;
		contentRef?: HTMLDivElement;
	} = $props();
</script>

<div class="modal-content" bind:this={contentRef}>
	{@render children()}
</div>
