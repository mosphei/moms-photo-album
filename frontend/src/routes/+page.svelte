<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { photopages } from '$lib/stores/photo-store';
	import Pagination from '$lib/components/Pagination.svelte';
	import Thumbnail from './Thumbnail.svelte';
	import PhotoViewer from './PhotoViewer.svelte';
	import PhotoEditor from './PhotoEditor.svelte';
	import { tick } from 'svelte';
	import Modal from '$lib/components/Modal.svelte';
	import type { Person } from '$lib/models/person';
	import PersonChooser from '$lib/components/PersonChooser.svelte';
	import { fly } from 'svelte/transition';
	import { clickOutside } from '$lib/click-outside';
	import { get } from 'svelte/store';

	let { currentPage, numPerPage, items, totalItems, criteria } = photopages;
	let last: number | undefined = $state(undefined);
	let currentPhotoIndex = $state(-1);
	let selectedPhotos: number[] = $state([]);
	let page = $state($currentPage);

	$effect(() => {
		if (page !== $currentPage) {
			currentPage.set(page);
		}
	});

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

	function handleThumbnailClick(e: MouseEvent, photo: Photo): void {
		e.preventDefault();
		currentPhotoIndex = $items.findIndex((p) => p.id === photo.id);
		tick().then((_) => viewdialog!.open());
	}

	function handlePrev(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		console.log('handlePrev');
		event.preventDefault();
		selectedPhotos = [];
		if (currentPhotoIndex < 1) {
			if (page > 1) {
				console.log('prev page');
				page = page - 1;
				currentPhotoIndex = $items.length - 1;
			} else {
				currentPhotoIndex = 0;
			}
		} else {
			currentPhotoIndex = currentPhotoIndex - 1;
		}
	}

	function handleNext(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		selectedPhotos = [];
		if (currentPhotoIndex >= $items.length - 1) {
			// need a new page
			if (!last || last > page) {
				page = page + 1;
				currentPhotoIndex = 0;
			}
		} else {
			currentPhotoIndex = currentPhotoIndex + 1;
		}
	}

	function handleLimitChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const x = parseInt(event.currentTarget.value);
		numPerPage.set(x);
	}
	// criteria
	let afterDate = $state($criteria.after ? $criteria.after.toLocaleDateString() : undefined);
	let beforeDate = $state($criteria.before ? $criteria.before.toLocaleDateString() : undefined);
	let q = $state($criteria.q);
	let searchTimerId: any = 0;

	let busy = $state(false);
	photopages.items.subscribe(()=>busy=false);

	function handleSearchChange(event: Event) {
		event.preventDefault();
		if (searchTimerId) {
			clearTimeout(searchTimerId);
		}
		busy=true;
		searchTimerId = setTimeout(() => {
			criteria.update((C) => {
				C.q = q;
				return C;
			});
		}, 300);
	}
	function handleAfterChange(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		const newval = event.currentTarget.value;
		// console.log('handleAfterChange', newval);
		if (newval) {
			criteria.update((C) => {
				C.after = new Date(newval);
				return C;
			});
		} else {
			criteria.update((C) => {
				C.after = undefined;
				return C;
			});
		}
	}
	function handleBeforeChange(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		const newval = event.currentTarget.value;
		console.log('handleBeforeChange', newval);
		if (newval) {
			criteria.update((C) => {
				C.before = new Date(newval);
				return C;
			});
		} else {
			criteria.update((C) => {
				C.before = undefined;
				return C;
			});
		}
	}
	let filterPersons: Person[] = $state([]);
	function addFilterPerson(person: Person) {
		filterPersons = Array.from(new Set([...filterPersons, person]));
		criteria.update((C) => {
			C.person_ids = filterPersons.map((p) => p.id);
			return C;
		});
	}
	function removeFilterPerson(person: Person) {
		filterPersons = filterPersons.filter((p) => p.id !== person.id);
		criteria.update((C) => {
			C.person_ids = filterPersons.map((p) => p.id);
			return C;
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
	let sortInput = $state(getInitialSort($criteria.sortBy, $criteria.sortDescending));

	function handleSortChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const newval = event.currentTarget.value as (typeof sort_options)[number];
		// console.log('handleSortChange', newval);
		criteria.update((C) => {
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

	// allow for shift-click to select multiple items
	function handleCheckboxClick(
		event: MouseEvent & { currentTarget: EventTarget & HTMLInputElement }
	) {
		console.log('handleCheckboxClick!', event);
		if (event.shiftKey) {
			if (selectedPhotos.length > 0) {
				const last_chosen = selectedPhotos[selectedPhotos.length - 1];
				const idx = $items.findIndex((p) => p.id === last_chosen);
				const currentId = parseInt(event.currentTarget.value);
				const currentIdx = $items.findIndex((p) => p.id === currentId);
				const [first, last] = currentIdx > idx ? [idx, currentIdx] : [currentIdx, idx];
				selectedPhotos = Array.from(
					new Set([
						...selectedPhotos,
						...$items.filter((itm, i) => i >= first && i <= last).map((itm) => itm.id)
					])
				);
			}
		}
	}
	let editDialog: Modal | undefined = $state(undefined);
	let photosToEdit: Photo[] = $state([]);
	function handleEditClick(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		photosToEdit = $items.filter((p) => selectedPhotos.includes(p.id));
		editDialog!.open();
	}
	let viewdialog: Modal | undefined = $state(undefined);

	function handleOnSave(): void {
		editDialog?.close();
		selectedPhotos = [];
		photopages.refresh();
	}

	let showFilterMenu = $state(false);
</script>

<svelte:head><title>PhotoDB - Moms Photo Album</title></svelte:head>
<div id="filters" class="row g-3 align-items-center mb-2">
	<div class="col-auto">
		<button class="btn btn-primary" onclick={() => (showFilterMenu = true)}> Filter </button>
	</div>
	{#if $criteria.after}
		<div class="col-auto">
			<button class="btn btn-outline-secondary">
				After {$criteria.after.toLocaleDateString()}
				<span class="bi bi-x"> </span>
			</button>
		</div>
	{/if}
	{#if filterPersons.length}
		<div class="col-auto">
			{#each filterPersons as p}
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
	<form class="col-auto" 
		onsubmit={handleSearchChange}
		onreset={handleSearchChange}
	>
		<div class="input-group">
			<input
				class="form-control"
				style="width:10rem;"
				placeholder="search descriptions"
				bind:value={q}
			/>
			{#if q}
			<button class="btn btn-outline-secondary" type="reset">
				Clear
			</button>
			{/if}
			<button class="btn btn-outline-primary" disabled={busy}>
				Search
			</button>
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
							{#each filterPersons as p}
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
<div>
	{($currentPage - 1) * $numPerPage + 1}
	to {($currentPage - 1) * $numPerPage + $numPerPage}
	of {$totalItems}
</div>
{#if $items.length == 0}
	<div class="alert alert-info m-3">No photos found.</div>
{/if}
{#each $items as photo}
	<div style="float:left; position:relative; padding:.5rem">
		<Thumbnail {photo} onclick={(e) => handleThumbnailClick(e, photo)} />
		<label style="position:absolute;top:0;left:0;padding:1rem" for="select_{photo.id}">
			<input
				type="checkbox"
				id="select_{photo.id}"
				bind:group={selectedPhotos}
				value={photo.id}
				onclick={handleCheckboxClick}
			/>
		</label>
	</div>
{/each}
{#if currentPhotoIndex >= 0}
	{@const photo = $items[currentPhotoIndex]}
	{#if photo}
		<Modal bind:this={viewdialog}>
			{#snippet title()}
				{photo.date_taken.toLocaleDateString()}
				{photo.filename}
			{/snippet}
			<div class="d-flex justify-content-center">
				<PhotoViewer {photo} />
			</div>
			{#snippet footer()}
				<button type="button" class="btn btn-primary" onclick={handlePrev}>Prev</button>
				<button type="button" class="btn btn-primary" onclick={handleNext}>Next</button>
			{/snippet}
		</Modal>
	{/if}
{/if}
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
	{#if selectedPhotos.length}
		<div class="col-auto">
			<button class="btn btn-primary" onclick={handleEditClick} type="button">
				Edit
				{selectedPhotos.length}
			</button>
			<button class="btn btn-secondary" onclick={() => (selectedPhotos = [])} type="button">
				Deselect
			</button>
		</div>
	{/if}
</div>

<Modal bind:this={editDialog} closedBy="closerequest">
	{#snippet title()}
		Edit {photosToEdit.length} Item{photosToEdit.length == 1 ? '' : 's'}
	{/snippet}
	<PhotoEditor photos={photosToEdit} onsave={handleOnSave} oncancel={() => editDialog?.close()} />
</Modal>
<DebugPanel value={{ currentPage: $currentPage, photos: $items }} />
