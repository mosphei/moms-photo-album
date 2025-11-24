<script lang="ts">
	import '../app.scss';
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import Login from '$lib/components/Login.svelte';
	import { me } from '$lib/stores/me-store';
	import Nav from '$lib/components/nav/Nav.svelte';
	import { session } from '$lib/stores/session-store';

	let { children } = $props();
	const loggedIn = session.loggedIn;

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
	{#if $loggedIn}
		{@render children?.()}
	{:else if $loggedIn === false}
		<Login />
	{:else} 
		<div>Please wait...</div>
	{/if}
</div>
<DebugPanel value={{ xloggedIn:$loggedIn }}>
	<button onclick={handleTest}>Test Auth</button>
</DebugPanel>