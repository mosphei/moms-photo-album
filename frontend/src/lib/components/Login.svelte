<script lang="ts">
	import { me } from '$lib/stores/me-store';

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
			localStorage.setItem('access_token', result.access_token);
			me.refresh();
		} catch (err) {
			console.log(`got err`, err);
			alert(err);
		}
	}
</script>

<div class="card">
	<div class="card-body">
		<h3 class="card-title">Log in</h3>
		<form bind:this={form} action="/api/users/token" method="POST" onsubmit={handleSubmit}>
			<input type="hidden" name="grant_type" value="password" />
			<input type="hidden" name="scope" value="" />
			<input type="hidden" name="client_id" value="" />
			<input type="hidden" name="client_secret" value="" />
			<div class="mb-3">
				<label for="username">Username:</label>
				<input
					type="text"
					id="username"
					name="username"
					autocomplete="off"
					bind:value={username}
					required
					class="form-control"
				/>
			</div>
			<div class="mb-3">
				<label for="password">Password:</label>
				<input
					type="password"
					id="password"
					name="password"
					bind:value={password}
					required
					class="form-control"
				/>
			</div>
			<button>Submit</button>
		</form>
	</div>
</div>
