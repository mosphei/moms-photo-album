<script lang="ts">
	import { me } from '$lib/stores/me-store';

	let form: HTMLFormElement;
	let username = $state('');
	let password = $state('');
	let message: { type: string; detail: string } | null = $state(null);

	async function handleSubmit(
		event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }
	) {
		event.preventDefault();
		const formData = new FormData(form);
		console.log(formData);
		try {
			const response = await fetch('/api/users/login', {
				method: 'POST',
				body: formData
			});
			const result = await response.text();
			console.log(result);
			if (!response.ok) {
				throw new Error(result);
			}
			message = { type: 'success', detail: 'Success!' };

			me.refresh();
		} catch (err: any) {
			console.log(`got err`, err);
			let msg = {
				type: 'error',
				detail: ''
			};
			try {
				const result = JSON.parse(err);
				if ('detail' in err) {
					msg.detail = result.detail;
				} else {
					msg.detail = result;
				}
			} catch {
				msg.detail = err;
			}
			message = msg;
		}
	}
</script>

<div class="card">
	<div class="card-body">
		<h3 class="card-title">Log in</h3>
		<form bind:this={form} onsubmit={handleSubmit} action="/api/users/login">
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
			{#if message}
				<div class="alert {message.type == 'error' ? 'alert-danger' : 'alert-secondary'} mb-2">
					{message.detail}
				</div>
			{/if}
			<button class="btn btn-primary">Submit</button>
		</form>
	</div>
</div>
