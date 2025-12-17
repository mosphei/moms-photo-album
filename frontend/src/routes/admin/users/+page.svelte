<script lang="ts">
	import { errorAlert, progressAlert } from '$lib/alerts';
	import PageTitle from '$lib/components/PageTitle.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { PaginatedStore } from '$lib/models/paginated-store';
	import type { User } from '$lib/models/user';
	import { fetchApi } from '$lib/stores/common-store';
	import { dateTimeReviver } from '$lib/utils';
	import { onMount } from 'svelte';
	import NewUserForm from './NewUserForm.svelte';
	import EditUserForm from './EditUserForm.svelte';
	const userstore = new PaginatedStore<User>(async (page: number, numPerPage: number) => {
		const offset = (page - 1) * numPerPage;
		const urlParams = new URLSearchParams({
			offset: `${offset}`,
			limit: `${numPerPage}`
		});
		const url = '/api/admin/users?' + urlParams.toString();
		try {
			const response = await fetchApi(url, {
				headers: { accept: 'application/json' }
			});
			if (!response) {
				throw new Error('no response');
			}
			const result = JSON.parse(response, dateTimeReviver);
			return result;
		} catch (error) {
			errorAlert('unable to fetch users', error, 15000);
		}
	});

	let { currentItems, currentPage, numPerPage, totalCount, lastPage } = userstore;
	let page = $state($currentPage);
	let selectedUserId: number | undefined = $state();

	function handleAddClose(): void {
		// we should really return a user id and highlight the new user
		userstore.refresh();
		selectedUserId = undefined;
	}

	onMount(() => userstore.refresh());
</script>

<PageTitle title="Admin - Users">
	<h1>Admin Users</h1>
</PageTitle>

<div>
	{($currentPage - 1) * $numPerPage + 1}
	to {($currentPage - 1) * $numPerPage + $numPerPage}
	of {$totalCount}
</div>

<div class="list-group" style="width: 25rem;">
	{#each $currentItems as user}
		{@const editing = user.id == selectedUserId}
		<div class={{ 'list-group-item': true, editing }}>
			<div class="d-flex justify-content-between w-100">
				<h5 class="mb-2">
					{user.username}
					{#if user.admin}
						- Admin
					{/if}
				</h5>
				{#if editing}
					<button
						class="btn btn-outline-secondary"
						type="button"
						onclick={() => (selectedUserId = undefined)}
					>
						<span class="visually-hidden">cancel</span>
						<span class="bi bi-x"></span>
					</button>
				{:else}
					<button
						class="btn btn-outline-secondary"
						type="button"
						onclick={() => (selectedUserId = user.id)}
					>
						<span class="visually-hidden">edit</span>
						<span class="bi bi-pencil"></span>
					</button>
				{/if}
			</div>
			{#if editing}
				<EditUserForm {user} onclose={handleAddClose} />
			{:else}
				<p class="mb-1">Some placeholder content in a paragraph.</p>
			{/if}
		</div>
	{/each}
	<div class="list-group-item">
		{#if selectedUserId == 0}
			<NewUserForm onclose={handleAddClose} />
		{:else}
			<button class="btn btn-primary" onclick={() => (selectedUserId = 0)}> Add New User </button>
		{/if}
	</div>
	{#if $totalCount == undefined || $totalCount > $numPerPage}
		<Pagination bind:page last={$lastPage} width={5} />
	{/if}
</div>

<style>
	.editing {
		border-color: var(--mo-primary);
		border: solid 1px var(--mo-primary);
	}
</style>
