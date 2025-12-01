<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { photopages } from '$lib/stores/photo-store';
	import { onMount, tick } from 'svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import Thumbnail from './Thumbnail.svelte';
	import PhotoViewer from './PhotoViewer.svelte';

	let dialog: HTMLDialogElement;
	let { currentPage, numPerPage, items, totalItems } = photopages;
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
		dialog.showModal();
	}

	function handlePrev(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		console.log('handlePrev');
		event.preventDefault();
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

	function handleEditClick(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		throw new Error('Function not implemented.');
	}
</script>

<div id="filters" class="row g-3 align-items-center">
	<div class="col-auto">Filter/Sort</div>
	<!-- by date -->
	<div class="col-auto">
		<div class="input-group">
			<select class="form-select" style="width: 7rem;">
				<option>After:</option>
				<option>Before:</option>
			</select>
			<input type="date" class="form-control" style="width: 10rem;" />
		</div>
	</div>
</div>
{#each $items as photo}
	<div style="float:left; position:relative; padding:.5rem">
		<Thumbnail {photo} onclick={(e) => handleThumbnailClick(e, photo)} />
		<input
			type="checkbox"
			style="position:absolute;top:1rem;left:1rem"
			bind:group={selectedPhotos}
			value={photo.id}
		/>
	</div>
{/each}
<dialog bind:this={dialog} closedby="any">
	{#if currentPhotoIndex >= 0}
		{@const photo = $items[currentPhotoIndex]}
		{#if photo}
			<div class="modal-content">
				<div class="modal-header">
					<h5 class="modal-title">
						{photo.date_taken.toLocaleDateString()}
						{photo.filename}
					</h5>
					<button class="btn-close" aria-label="Close" onclick={() => dialog.close()}></button>
				</div>
				<div class="modal-body mb-2 d-flex justify-content-center">
					<PhotoViewer {photo} />
				</div>
				<div class="modal-footer justify-content-between">
					<button type="button" class="btn btn-primary" onclick={handlePrev}>Prev</button>
					<button>Edit</button>
					<button type="button" class="btn btn-primary" onclick={handleNext}>Next</button>
				</div>
			</div>
		{/if}
	{/if}
</dialog>
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
			<button class="btn btn-primary" onclick={handleEditClick}>
				Edit
				{selectedPhotos.length}
			</button>
		</div>
	{/if}
</div>
<DebugPanel value={{ currentPage: $currentPage, photos: $items }} />

<style>
	dialog {
		/*width: 80%;*/
		border-radius: 6px;
		padding: 0.5rem;
		--mo-modal-header-border-color: var(--mo-primary);
		--mo-modal-header-border-width: 1px;
		--mo-heading-color: var(--mo-primary);
		--mo-modal-header-padding: 0.25rem;
		--mo-modal-padding: 0.25rem;
	}

	/* Styles for the backdrop */
	dialog::backdrop {
		background-color: rgba(0, 0, 100, 0.7);
		backdrop-filter: blur(3px);
	}
</style>
