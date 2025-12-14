<script lang="ts">
	import Login from '$lib/components/Login.svelte';
	import { me } from '$lib/stores/me-store';
	import { derived } from 'svelte/store';

	let { children } = $props();

	const isadmin = derived(me, (ME) => ME?.admin);
</script>

{#if $me === undefined}
	<div class="alert alert-info">Please wait...</div>
{:else if $isadmin}
	{@render children?.()}
{:else}
	<Login />
{/if}
