<script lang="ts">
	import { errorAlert, progressAlert } from '$lib/alerts';
	import type { User } from '$lib/models/user';
	import { slide } from 'svelte/transition';

	let { user, onclose }: { user: User; onclose: () => void } = $props();
	let form: HTMLFormElement;
	let password = $state('');
	let password2 = $state('');

	async function handleSubmit(
		event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }
	) {
		event.preventDefault();
		const formData = new FormData(event.currentTarget);
		const msg = progressAlert('saving user change...');
		try {
			const response = await fetch(form.action, {
				headers: { accept: 'application/json ' },
				method: 'POST',
				body: formData
			});
			const result = await response.json();
			if (!response.ok) {
				throw new Error(`Error ${response.status}: ${response.statusText}`);
			}
			console.log(result);
			form.reset();
			onclose?.();
		} catch (error) {
			errorAlert('unable to save user data', error, 10000);
		} finally {
			msg.dismiss();
		}
	}
</script>

<form bind:this={form} onsubmit={handleSubmit} action="/api/admin/users/" method="post">
	<input type="hidden" value={user.id} name="id" />
	<input type="hidden" value={user.username} name="username" />
	<div class="mb-2 form-check">
		<input
			type="checkbox"
			class="form-check-input"
			id="admin"
			name="admin"
			value="True"
			checked={user.admin}
		/>
		<label class="form-check-label" for="admin">Admin</label>
	</div>
	<div class="mb-2">
		<label for="password">Update Password (optional):</label>
		<input
			type="password"
			class="form-control"
			id="password"
			name="password"
			bind:value={password}
			minlength="10"
			title="Password must be at least 10 characters long"
		/>
		<div class="invalid-feedback">Password must be at least 10 characters.</div>
	</div>
	{#if password.length}
		<div class="mb-2 has-validation" transition:slide>
			<label for="password2">Password:</label>
			<input
				type="password"
				class={{ 'form-control': true, 'is-invalid': password2 && password2 !== password }}
				id="password2"
				bind:value={password2}
				pattern={password}
				required
			/>
			<div class="invalid-feedback">Passwords must match.</div>
		</div>
	{/if}
	<button class="btn btn-primary"> Save </button>
	<button class="btn btn-secondary" type="button" onclick={() => onclose?.()}> Cancel </button>
</form>
