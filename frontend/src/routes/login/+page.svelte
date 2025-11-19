<script lang="ts">
	let form: HTMLFormElement;
	let username = $state('');
	let password = $state('');

	async function handleSubmit(
		event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }
	) {
		event.preventDefault();
		const formData = new FormData(form);
		console.log(formData);
		try {
			const response = await fetch(form.action, {
				method: 'POST',
				body: formData
			});
			if (!response.ok) {
				const result = await response.text();
				throw new Error(result);
			}
			const result = await response.json();
			console.log(`got result`, result);
		} catch (err) {
			console.log(`got err`, err);
			alert(err);
		}
	}
</script>

<form bind:this={form} action="/api/users/token" method="POST" onsubmit={handleSubmit}>
	<input type="hidden" name="grant_type" value="password" />
	<input type="hidden" name="scope" value="" />
	<input type="hidden" name="client_id" value="" />
	<input type="hidden" name="client_secret" value="" />
	<input
		type="text"
		id="username"
		name="username"
		autocomplete="off"
		bind:value={username}
		required
	/>
	<input type="password" id="password" name="password" bind:value={password} required />
	<button>Submit</button>
</form>
