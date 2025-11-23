<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import Login from '$lib/components/Login.svelte';
	import { me } from '$lib/stores/me-store';

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

<nav>
	<h1>Moms Photo Album</h1>
	<a href="/">Browse</a>
	<a href="/upload">Upload</a>
</nav>
{#if $me}
	{@render children?.()}
{:else}
	<Login />
{/if}

<DebugPanel value={{ a: true }}>
	<button onclick={handleTest}>Test Auth</button>
</DebugPanel>
