<script lang="ts">
	import '../app.scss';
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import Login from '$lib/components/Login.svelte';
	import { me } from '$lib/stores/me-store';
	import Nav from '$lib/components/nav/Nav.svelte';

	let { children } = $props();

	function handleTest() {
		const token: string = localStorage.access_token || '';

		fetch('/api/users/me', {
			headers: {
				Authorization: `Bearer ${token}`
			}
		})
			.then((r) => r.text())
			.then((r) => alert(r))
			.catch((err) => {
				console.log('error getting user details', err);
				alert('err');
			});
	}
</script>

<Nav />

<div style="padding:1%">
	{#if $me}
		{@render children?.()}
	{:else}
		<Login />
	{/if}
</div>
<DebugPanel value={{ a: true }}>
	<button onclick={handleTest}>Test Auth</button>
</DebugPanel>

<style>
	nav {
		display: flex;
		align-items: baseline;
	}
	nav a {
		padding: 1em 0.25em;
	}
</style>
