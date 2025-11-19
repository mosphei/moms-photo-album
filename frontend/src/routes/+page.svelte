<script lang="ts">
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

<h1>Welcome to SvelteKit</h1>
<div>
	<button onclick={handleTest}>Test Auth</button>
</div>
