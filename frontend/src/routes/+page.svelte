<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { photopages } from '$lib/stores/photo-store';
	import Pagination from '$lib/components/Pagination.svelte';
	import Thumbnail from './Thumbnail.svelte';
	import PhotoViewer from './PhotoViewer.svelte';
	import PhotoEditor from './PhotoEditor.svelte';
	import { tick, type Snippet, type SvelteComponent } from 'svelte';
	import Modal from '$lib/components/Modal.svelte';

	let dialog: HTMLDialogElement;
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

	let afterDate = $state($criteria.after ? $criteria.after.toLocaleDateString() : undefined);
	let beforeDate = $state($criteria.before ? $criteria.before.toLocaleDateString() : undefined);
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
</script>

<div id="filters" class="row g-3 align-items-center mb-2">
	<div class="col-auto">Filter/Sort</div>
	<!-- by date -->
	<div class="col-auto">
		<div class="input-group">
			<span class="input-group-text">After:</span>
			<input
				type="date"
				class="form-control"
				style="width: 10rem;"
				bind:value={afterDate}
				onchange={handleAfterChange}
			/>
			<span class="input-group-text">Before:</span>
			<input
				type="date"
				class="form-control"
				style="width: 10rem;"
				bind:value={beforeDate}
				onchange={handleBeforeChange}
			/>
		</div>
	</div>
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
</div>
{#if $items.length == 0}
	<div class="alert alert-info m-3">No photos found.</div>
{/if}
{#each $items as photo}
	<div style="float:left; position:relative; padding:.5rem">
		<Thumbnail {photo} onclick={(e) => handleThumbnailClick(e, photo)} />
		<input
			type="checkbox"
			style="position:absolute;top:1rem;left:1rem"
			bind:group={selectedPhotos}
			value={photo.id}
			onclick={handleCheckboxClick}
		/>
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
	<PhotoEditor
		photos={photosToEdit}
		onsave={() => editDialog?.close()}
		oncancel={() => editDialog?.close()}
	/>
</Modal>
<DebugPanel value={{ currentPage: $currentPage, photos: $items }} />
