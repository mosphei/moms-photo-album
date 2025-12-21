<script lang="ts">
	import { errorAlert, progressAlert } from '$lib/alerts';
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import type { Person } from '$lib/models/person';
	import { peopleStore, peopleCriteria, savePerson } from '$lib/stores/people-store';
	import { onMount } from 'svelte';

	let { currentPage, numPerPage, currentItems, totalCount, lastPage } = peopleStore;
	let page = $state($currentPage);
	let last: number | undefined = $state(undefined);
	let q = $state($peopleCriteria.q);
	let sortDescending = $state(false);
	// for editing person
	let editPerson: Person | undefined = $state();

	function setLastPage(total_count: number | null, limit: number) {
		if (total_count && limit > 0) {
			last = Math.ceil(total_count / limit);
			if (page > last) {
				page = last;
			}
		}
	}

	function handleLimitChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const x = parseInt(event.currentTarget.value);
		peopleStore.setNumPerPage(x);
	}

	$effect(() => {
		console.log(`q=${q}`);
		peopleCriteria.update((C) => {
			if (q?.length) {
				C.q = q;
			} else {
				C.q = undefined;
			}
			return C;
		});
	});

	function handleSortChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		peopleCriteria.update((C) => {
			if (q?.length) {
				C.q = q;
			} else {
				C.q = undefined;
			}
			return C;
		});
	}

	$effect(() => {
		peopleStore.setCurrentPage(page);
	});

	onMount(() => {
		peopleStore.refresh();
	});

	async function handleSave(prson: Person | undefined) {
		console.log('handleSave');
		if (prson) {
			const msg = progressAlert('saving person info...');
			try {
				const x = await savePerson(prson);
				editPerson = undefined;
			} catch (error) {
				errorAlert(`unable to save person ${prson?.id}`, error, 15000);
			} finally {
				msg.dismiss();
			}
		}
	}
</script>

<svelte:head><title>PhotoDB - People</title></svelte:head>
<h1>People</h1>
<div id="filters" class="row g-3 align-items-center mb-2">
	<div class="col-auto">Filter/Sort</div>
	<!-- by name -->
	<div class="col-auto">
		<div class="input-group">
			<input type="text" name="q" bind:value={q} placeholder="Name" class="form-control" />
			{#if q}
				<button class="btn btn-primary" onclick={() => (q = '')} aria-label="clear search"
					><span class="bi bi-x"></span></button
				>
			{/if}
		</div>
	</div>
	<!-- sort -->
	<div class="col-auto">
		<div class="input-group">
			<span class="input-group-text">Sort:</span>
			<select
				name="sort"
				bind:value={sortDescending}
				class="form-select"
				onchange={handleSortChange}
			>
				<option value={false}>Ascending</option>
				<option value={true}>Descending</option>
			</select>
		</div>
	</div>
</div>
<p class="lead">
	{($currentPage - 1) * $numPerPage + 1}-{$currentPage * $numPerPage}
	{#if $totalCount}
		of {$totalCount}
	{/if}
</p>
{#snippet viewPersonListItem(person: Person)}
	<div class="list-group-item">
		<div class="d-flex w-100">
			<h5 class="mb-1">
				{person.name}
			</h5>
			<span style="flex:1"></span>

			<button
				class="btn btn-secondary"
				type="button"
				title="Edit"
				onclick={() => (editPerson = JSON.parse(JSON.stringify(person)))}
			>
				<span class="bi bi-pencil"></span>
				Edit
			</button>
		</div>
		{#if person.past_names?.length}
			<p class="mb-1">Other Names: {person.past_names}</p>
		{/if}
		{#if person.photo_count}
			<small>Appears in {person.photo_count} photo{person.photo_count == 1 ? '' : 's'}</small>
		{/if}
	</div>
{/snippet}
{#snippet editPersonListItem(person: Person)}
	<div class="list-group-item">
		<div class="d-flex w-100">
			<h5 class="mb-1">Edit Person</h5>
			<span style="flex:1"></span><button
				class="btn btn-primary me-2"
				type="button"
				title="Edit"
				onclick={() => handleSave(editPerson)}
			>
				<span class="bi bi-floppy"></span>
				Save
			</button>
			<button
				class="btn btn-secondary"
				type="button"
				title="Edit"
				onclick={() => (editPerson = undefined)}
			>
				Cancel
			</button>
		</div>
		<div class="mb-1">
			<label for="name">Name:</label>
			<input bind:value={editPerson!.name} class="form-control" name="name" />
		</div>
		<div class="mb-1">
			<label for="pastnames">Other Names:</label>
			<input class="form-control" bind:value={editPerson!.past_names} name="pastnames" />
		</div>
	</div>
{/snippet}
<!-- the list of people -->
<div class="list-group mb-3">
	{#if $currentItems.length == 0}
		<div class="list-group-item">No people found.</div>
	{/if}
	{#each $currentItems as person}
		{#if editPerson?.id == person.id}
			{@render editPersonListItem(person)}
		{:else}
			{@render viewPersonListItem(person)}
		{/if}
	{/each}
</div>
<!-- footer -->
<div style="clear: both;position:sticky;bottom:4px" class="row g-3">
	<div class="col-auto">
		<Pagination {last} bind:page />
	</div>
	<div class="col-auto">
		<div class="input-group">
			<span class="input-group-text"> Show </span>
			<select name="nmn" value={$numPerPage} onchange={handleLimitChange} class="form-select">
				{#each [10, 20, 50, 100] as val}
					<option>{val}</option>
				{/each}
			</select>
		</div>
	</div>
</div>
<DebugPanel value={{ criteria: $peopleCriteria }} />
