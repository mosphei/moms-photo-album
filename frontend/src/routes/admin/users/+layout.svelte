<script lang="ts">
	import PageTitle from '$lib/components/PageTitle.svelte';

	let { children } = $props();
</script>

{@render children?.()}
