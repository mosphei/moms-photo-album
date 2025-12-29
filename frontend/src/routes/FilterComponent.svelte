<script lang="ts">
	import { clickOutside } from '$lib/click-outside';
	import PersonChooser from '$lib/components/PersonChooser.svelte';
	import type { Person } from '$lib/models/person';
	import type { IPhotoCriteria } from '$lib/stores/photo-store';
	import type { Writable } from 'svelte/store';
	import { fly } from 'svelte/transition';

	let { criteria }: { criteria: Writable<IPhotoCriteria | undefined> } = $props();
	let showFilterMenu = $state(false);
	let afterDate = $state($criteria?.after ? $criteria.after.toLocaleDateString() : undefined);
	let beforeDate = $state($criteria?.before ? $criteria.before.toLocaleDateString() : undefined);
	let q = $state($criteria?.q);
	let searchTimerId: any = 0;
	let busy = $state(false);

	function handleSearchChange(event: Event) {
		event.preventDefault();
		if (searchTimerId) {
			clearTimeout(searchTimerId);
		}
		busy = true;
		searchTimerId = setTimeout(() => {
			criteria.update((C) => {
				const x: any = C || {};
				x.q = q;
				return x;
			});
		}, 300);
	}
	function handleAfterChange(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		const newval = event.currentTarget.value;
		// console.log('handleAfterChange', newval);
		if (newval) {
			criteria.update((C) => {
				const c: any = C || {};
				c.after = new Date(newval);
				return c;
			});
		} else {
			criteria.update((C) => {
				const c: any = C || {};
				c.after = undefined;
				return c;
			});
		}
	}
	function handleBeforeChange(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		const newval = event.currentTarget.value;
		console.log('handleBeforeChange', newval);
		if (newval) {
			criteria.update((C) => {
				const c: any = C || {};
				c.before = new Date(newval);
				return c;
			});
		} else {
			criteria.update((C) => {
				const c: any = C || {};
				c.before = undefined;
				return c;
			});
		}
	}
	let filterPersons: Person[] = $state([]);
	function addFilterPerson(person: Person) {
		filterPersons = Array.from(new Set([...filterPersons, person]));
		criteria.update((C) => {
			const c: any = C || {};
			c.person_ids = filterPersons.map((p) => p.id);
			return c;
		});
	}
	function removeFilterPerson(person: Person) {
		filterPersons = filterPersons.filter((p) => p.id !== person.id);
		criteria.update((C) => {
			const c: any = C || {};
			c.person_ids = filterPersons.map((p) => p.id);
			return c;
		});
	}

	// sorting
	const sort_options = [
		'Oldest',
		'Newest',
		'First Uploaded',
		'Last Uploaded',
		'Recently Edited',
		'Unedited'
	] as const;
	function getInitialSort(
		sortBy: string | undefined,
		descending: boolean | undefined
	): (typeof sort_options)[number] {
		switch (sortBy) {
			case 'date_taken':
				if (descending) {
					return 'Newest';
				}
				return 'Oldest';
			case 'date_uploaded':
				if (descending) {
					return 'Last Uploaded';
				}
				return 'First Uploaded';
			case 'date_updated':
				if (descending) {
					return 'Recently Edited';
				}
				return 'Unedited';
		}
		// default sort
		return 'Oldest';
	}
	let sortInput = $state(
		getInitialSort($criteria?.sortBy || 'date_taken', $criteria?.sortDescending || false)
	);

	function handleSortChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const newval = event.currentTarget.value as (typeof sort_options)[number];
		// console.log('handleSortChange', newval);
		criteria.update((oldval) => {
			const C: any = oldval || {};
			switch (newval) {
				case 'Oldest':
					C.sortBy = 'date_taken';
					C.sortDescending = false;
					break;
				case 'Newest':
					C.sortBy = 'date_taken';
					C.sortDescending = true;
					break;
				case 'First Uploaded':
					C.sortBy = 'date_uploaded';
					C.sortDescending = false;
					break;
				case 'Last Uploaded':
					C.sortBy = 'date_uploaded';
					C.sortDescending = true;
					break;
				case 'Recently Edited':
					C.sortBy = 'date_updated';
					C.sortDescending = true;
					break;
				case 'Unedited':
					C.sortBy = 'date_updated';
					C.sortDescending = false;
			}
			console.log('criteria', C);
			return C;
		});
	}
</script>

<div id="filters" class="row g-3 align-items-center mb-2">
	<div class="col-auto">
		<button class="btn btn-primary" onclick={() => (showFilterMenu = true)}> Filter </button>
	</div>
	{#if $criteria?.after}
		<div class="col-auto">
			<button class="btn btn-outline-secondary">
				After {$criteria.after.toLocaleDateString()}
				<span class="bi bi-x"> </span>
			</button>
		</div>
	{/if}
	{#if filterPersons.length}
		<div class="col-auto">
			{#each filterPersons as p (p.id)}
				<button
					class="btn btn-outline-secondary"
					title="remove"
					onclick={() => removeFilterPerson(p)}
				>
					{p.name}
					<span class="bi bi-x"></span>
				</button>
			{/each}
		</div>
	{/if}
	<!-- Search -->
	<form class="col-auto" onsubmit={handleSearchChange} onreset={handleSearchChange}>
		<div class="input-group">
			<input
				class="form-control"
				style="width:10rem;"
				placeholder="search descriptions"
				bind:value={q}
			/>
			{#if q}
				<button class="btn btn-outline-secondary" type="reset"> Clear </button>
			{/if}
			<button class="btn btn-outline-primary" disabled={busy}> Search </button>
		</div>
	</form>
	<!-- sort -->
	<div class="col-auto">
		<div class="input-group">
			<span class="input-group-text">Sort:</span>
			<select name="sort" bind:value={sortInput} class="form-select" onchange={handleSortChange}>
				{#each sort_options as opt}
					<option>{opt}</option>
				{/each}
			</select>
		</div>
	</div>
	{#if showFilterMenu}
		<div
			transition:fly|local={{ x: -200, duration: 500 }}
			class="offcanvas offcanvas-start show"
			tabindex="-1"
			id="offcanvas"
			aria-labelledby="offcanvasLabel"
			use:clickOutside={() => (showFilterMenu = false)}
		>
			<div class="offcanvas-header">
				<h5 class="offcanvas-title" id="offcanvasLabel">Filter</h5>
				<button
					type="button"
					class="btn-close"
					data-bs-dismiss="offcanvas"
					aria-label="Close"
					onclick={() => (showFilterMenu = false)}
				></button>
			</div>
			<div class="offcanvas-body">
				<div class="mb-3">
					<label for="after">After:</label>
					<input
						type="date"
						class="form-control"
						style="width: 10rem;"
						bind:value={afterDate}
						onchange={handleAfterChange}
						name="after"
					/>
				</div>

				<div class="mb-3">
					<label for="before">Before:</label>
					<input
						name="before"
						type="date"
						class="form-control"
						style="width: 10rem;"
						bind:value={beforeDate}
						onchange={handleBeforeChange}
					/>
				</div>
				<div class="mb-3" style="position:relative">
					{#if filterPersons.length}
						<div>
							{#each filterPersons as p (p.id)}
								<button
									class="btn btn-outline-secondary"
									title="remove"
									onclick={() => removeFilterPerson(p)}
								>
									{p.name}
									<span class="bi bi-x"></span>
								</button>
							{/each}
						</div>
					{/if}
					<label for="person"> By person </label>
					<PersonChooser onselect={(p) => addFilterPerson(p)} />
				</div>
			</div>
		</div>
	{/if}
	<!-- sort -->
</div>
