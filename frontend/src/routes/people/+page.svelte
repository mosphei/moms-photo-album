<script lang="ts">
	import Pagination from '$lib/components/Pagination.svelte';
	import { peoplepages } from '$lib/stores/people-store';
	import { onMount } from 'svelte';

	let { currentPage, numPerPage, items, totalItems, criteria } = peoplepages;
	let page = $state($currentPage);
	let last: number | undefined = $state(undefined);
	let q = $state('');
	let sortDescending = $state(false);

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

	onMount(() => {
		peoplepages.refresh();
	});
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
{#if $items.length == 0}
	<div class="alert alert-info m-3">No people found.</div>
{/if}
{#each $items as person}
	<div class="card mb-3">
		<div class="card-body">
			<h5 class="card-title">{person.name} ({person.id})</h5>
			<p class="card-text">{person.past_names || ''}</p>
		</div>
	</div>
{/each}
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
