<script lang="ts">
	import Pagination from '$lib/components/Pagination.svelte';
	import type { Person } from '$lib/models/person';
	import { peoplepages } from '$lib/stores/people-store';
	import { onMount } from 'svelte';

	let { currentPage, numPerPage, items, totalItems, criteria } = peoplepages;
	let page = $state($currentPage);
	let last: number | undefined = $state(undefined);
	let q = $state('');
	let sortDescending = $state(false);
    // for editing person
    let editPerson:Person|undefined = $state();

	function setLastPage(total_count: number | null, limit: number) {
		if (total_count && limit > 0) {
			last = Math.ceil(total_count / limit);
			if (page > last) {
				page = last;
			}
		}
	}
	totalItems.subscribe((TOTAL) => setLastPage(TOTAL, $numPerPage));
	numPerPage.subscribe((LIMIT) => setLastPage($totalItems, LIMIT));

	function handleLimitChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const x = parseInt(event.currentTarget.value);
		numPerPage.set(x);
	}

	function handleNameInput(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		peoplepages.criteria.update((C) => {
			if (q.length) {
				C.q = q;
			} else {
				C.q = undefined;
			}
			return C;
		});
	}

	function handleSortChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		peoplepages.criteria.update((C) => {
			if (q.length) {
				C.q = q;
			} else {
				C.q = undefined;
			}
			return C;
		});
	}

    $effect(()=>{
        currentPage.set(page);
    });

	onMount(() => {
		peoplepages.refresh();
	});


	function savePerson(editPerson: Person | undefined): any {
		throw new Error('Function not implemented.');
	}
</script>

<svelte:head><title>PhotoDB - People</title></svelte:head>
<h1>People</h1>
<div id="filters" class="row g-3 align-items-center mb-2">
	<div class="col-auto">Filter/Sort</div>
	<!-- by date -->
	<div class="col-auto">
		<input
			type="text"
			name="q"
			bind:value={q}
			placeholder="Name"
			oninput={handleNameInput}
			class="form-control"
		/>
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
	{#if $totalItems}
		of {$totalItems}
	{/if}
</p>
{#snippet viewPersonListItem(person:Person)}
    <div class="list-group-item">
        <div class="d-flex w-100">
            <h5 class="mb-1">
                
                {person.name}
                
            </h5>
            <span style="flex:1"></span>
                    
            <button class="btn btn-secondary" type="button" title="Edit" onclick={()=>editPerson = person}>
                <span class="bi bi-pencil"></span>
                Edit
            </button>
        </div>
        {#if person.past_names?.length}
            <p class="mb-1">Other Names: {person.past_names}</p>
        {/if}
    </div>
{/snippet}
{#snippet editPersonListItem(person:Person)}
<div class="list-group-item">
    <div class="d-flex w-100">
        <h5 class="mb-1">Edit Person</h5>
        <span style="flex:1"></span><button class="btn btn-primary me-2" type="button" title="Edit" onclick={()=>savePerson(editPerson)}>
        <span class="bi bi-floppy"></span>
            Save
        </button>
        <button class="btn btn-secondary" type="button" title="Edit" onclick={()=>editPerson = undefined}>
            
            Cancel
        </button>
    </div>    
    <div class="mb-1">
        <label for="name">Name:</label>
        <input bind:value={editPerson!.name} class="form-control" name="name">
    </div>
    <div class="mb-1">
        <label for="pastnames">Other Names:</label>
        <input class="form-control" bind:value={editPerson!.past_names} name="pastnames">
    </div> 
</div>
{/snippet}
<div class="list-group">
	{#if $items.length == 0}
		<div class="list-group-item">No people found.</div>
	{/if}
	{#each $items as person}
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
