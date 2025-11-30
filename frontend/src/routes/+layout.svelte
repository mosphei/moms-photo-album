<script lang="ts">
	import '../app.scss';
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import Login from '$lib/components/Login.svelte';
	import Nav from '$lib/components/nav/Nav.svelte';
	import { session } from '$lib/stores/session-store';
	import { fetchApi } from '$lib/stores/common-store';

	let { children } = $props();
	const loggedIn = session;

	async function handleTest() {
		const txt = await fetchApi('/api/users/me');
		alert(txt);
	}
</script>

<Nav />

<div style="padding:1%">
	{#if $loggedIn}
		{@render children?.()}
	{:else if $loggedIn === false}
		<Login />
	{:else}
		<div>Please wait...</div>
	{/if}
</div>
<!--
<DebugPanel value={{ xloggedIn: $loggedIn }}>
	<button class="btn btn-light" onclick={handleTest}>Test Auth</button>
</DebugPanel>
-->
