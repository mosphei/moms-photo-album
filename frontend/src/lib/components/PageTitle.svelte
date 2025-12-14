<script lang="ts">
	import type { Snippet } from 'svelte';

	let { title, children }: { title: string; children: Snippet } = $props();
</script>

<svelte:head>
	<title>{title} - PhotoDB</title>
</svelte:head>
<h1>
	{@render children()}
</h1>
