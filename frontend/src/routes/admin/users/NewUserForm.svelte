<script lang="ts">
	import { errorAlert, progressAlert } from '$lib/alerts';
	import type { UserCreate } from '$lib/models/user';
	import { slide } from 'svelte/transition';

	let { onclose = undefined }: { onclose?: () => void } = $props();

	let form: HTMLFormElement;
	let wasValidated = $state(false);
	let usernameConflict = $state(false);
	let userTimerId: any = 0;
	function handleUsernameInput(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		if (userTimerId) {
			clearTimeout(userTimerId);
		}
		if (username.length) {
			userTimerId = setTimeout(async () => {
				const url = `/api/admin/users/${username}`;
				console.log('checking for user ' + url);
				const response = await fetch(url, {
					headers: { accept: 'application/json' }
				});
				if (response.ok) {
					// oops this acct already exists
					usernameConflict = true;
				}
				if (response.status == 404) {
					usernameConflict = false;
				}
			}, 500);
		} else {
			usernameConflict = false;
		}
	}

	let username = $state('');
	let password = $state('');
	let password2 = $state('');
	async function handleAddUser(
		event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }
	) {
		event.preventDefault();

		if (password !== password2) {
			console.error('Passwords do not match!');
			alert('Passwords do not match!');
			return;
		}

		// Create a data object to send
		const data: UserCreate = {
			username,
			password
		};
		console.log('registering user', data);
		const msg = progressAlert('registering new user...');
		try {
			// Send the data using fetch API with POST method
			const response = await fetch('/api/users/register', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
					//accept: 'application/json'
				},
				body: JSON.stringify(data)
			});

			// Check if the request was successful
			if (!response.ok) {
				// Handle server errors (e.g., status 400, 401, 500)
				const errorData = await response.json();
				console.log(errorData);
				throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
			}

			const result = await response.json();
			console.log('Success:', result);
			onclose?.();
		} catch (error) {
			console.error('Error:', error);
			errorAlert(`Registration failed`, error, 10000);
		} finally {
			msg.dismiss();
		}
	}

	function handleCancel(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		form.reset();
		onclose?.();
	}
</script>

<form
	transition:slide
	onsubmit={handleAddUser}
	class={{ 'was-validated': wasValidated }}
	bind:this={form}
>
	<h5 class="mb-2">Add New User</h5>
	<div class="mb-2">
		<label for="username">Username:</label>
		<input
			type="text"
			id="username"
			class={{ 'form-control': true, 'is-invalid': usernameConflict }}
			bind:value={username}
			oninput={handleUsernameInput}
			required
		/>
		<div class="invalid-feedback">
			{#if usernameConflict}
				Username is already taken.
			{:else}
				Please enter a valid username.
			{/if}
		</div>
	</div>
	<div class="mb-2">
		<label for="password">Password:</label>
		<input
			type="password"
			class="form-control"
			id="password"
			bind:value={password}
			minlength="10"
			title="Password must be at least 10 characters long"
			required
		/>
		<div class="invalid-feedback">Password must be at least 10 characters.</div>
	</div>
	<div class="mb-2 has-validation">
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
	<button class="btn btn-primary" onclick={() => (wasValidated = true)}> Save </button>
	<button class="btn btn-secondary" onclick={handleCancel} type="reset"> Cancel </button>
</form>
