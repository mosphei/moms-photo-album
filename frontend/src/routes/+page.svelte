<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { paginatedPhotos, photoCriteria } from '$lib/stores/photo-store';
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
	import FilterComponent from './FilterComponent.svelte';

	let { currentPage, numPerPage, currentItems, totalCount, lastPage } = paginatedPhotos;
	let currentPhotoIndex = $state(-1);
	let selectedPhotos: number[] = $state([]);
	let page = $state($currentPage);

	$effect(() => {
		if (page !== $currentPage) {
			paginatedPhotos.setCurrentPage(page);
		}
	});
	currentPage.subscribe((C) => {
		if (page !== C) {
			page = C;
		}
	});

	function handleThumbnailClick(e: MouseEvent, photo: Photo): void {
		e.preventDefault();
		currentPhotoIndex = $currentItems.findIndex((p) => p.id === photo.id);
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
				currentPhotoIndex = $currentItems.length - 1;
			} else {
				currentPhotoIndex = 0;
			}
		} else {
			currentPhotoIndex = currentPhotoIndex - 1;
		}
	}

	function handleNext(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		selectedPhotos = [];
		if (currentPhotoIndex >= $currentItems.length - 1) {
			// need a new page
			if (!$lastPage || $lastPage > page) {
				page = page + 1;
				currentPhotoIndex = 0;
			}
		} else {
			currentPhotoIndex = currentPhotoIndex + 1;
		}
	}

	function handleLimitChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const x = parseInt(event.currentTarget.value);
		if (x < 1) {
			paginatedPhotos.setNumPerPage(autoItems);
		} else {
			paginatedPhotos.setNumPerPage(x);
		}
	}
	// criteria

	// photopages.items.subscribe(() => (busy = false));

	// allow for shift-click to select multiple items
	function handleCheckboxClick(
		event: MouseEvent & { currentTarget: EventTarget & HTMLInputElement }
	) {
		console.log('handleCheckboxClick!', event);
		if (event.shiftKey) {
			if (selectedPhotos.length > 0) {
				const last_chosen = selectedPhotos[selectedPhotos.length - 1];
				const idx = $currentItems.findIndex((p) => p.id === last_chosen);
				const currentId = parseInt(event.currentTarget.value);
				const currentIdx = $currentItems.findIndex((p) => p.id === currentId);
				const [first, last] = currentIdx > idx ? [idx, currentIdx] : [currentIdx, idx];
				selectedPhotos = Array.from(
					new Set([
						...selectedPhotos,
						...$currentItems.filter((itm, i) => i >= first && i <= last).map((itm) => itm.id)
					])
				);
			}
		}
	}
	let editDialog: Modal | undefined = $state(undefined);
	let photosToEdit: Photo[] = $state([]);
	function handleEditClick(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		photosToEdit = $currentItems.filter((p) => selectedPhotos.includes(p.id));
		editDialog!.open();
	}
	let viewdialog: Modal | undefined = $state(undefined);

	function handleOnSave(): void {
		editDialog?.close();
		selectedPhotos = [];
	}

	let containerDiv: HTMLDivElement | undefined = $state();
	let footerDiv: HTMLDivElement | undefined = $state();
	let itemsPerPage = $state(0);
	let autoItems = $state(10);
	$effect(() => {
		if (itemsPerPage == 0) {
			paginatedPhotos.setNumPerPage(autoItems);
		}
	});
	let autoItemsTimer: any = 0;
	function getAutoItemsCount() {
		if (autoItemsTimer) {
			clearTimeout(autoItemsTimer);
		}
		setTimeout(() => {
			if (containerDiv && footerDiv) {
				const containerRect = containerDiv.getBoundingClientRect();
				const footerRect = footerDiv.getBoundingClientRect();
				const h = footerRect.top - containerRect.top;
				const w = containerRect.width;
				console.log(`(${w},${h})`);
				const itemsPerRow = Math.floor(w / 220);
				const itemRows = Math.floor(h / 200);
				autoItems = itemRows * itemsPerRow;
				console.log('autoItems', autoItems);
			} else {
				// try again
				getAutoItemsCount();
			}
		}, 100);
	}
	let innerWidth = $state(0);
	let innerHeight = $state(0);
	$effect(() => {
		if (innerWidth && innerHeight) {
			getAutoItemsCount();
		}
	});
</script>

<svelte:head><title>PhotoDB - Moms Photo Album</title></svelte:head>
<svelte:window bind:innerWidth bind:innerHeight />
<FilterComponent criteria={photoCriteria} />

<div>
	{($currentPage - 1) * $numPerPage + 1}
	to {($currentPage - 1) * $numPerPage + $numPerPage}
	of {$totalCount}
</div>
<div bind:this={containerDiv} style="display: flex; flex-wrap:wrap">
	{#if $currentItems.length == 0}
		<div class="alert alert-info m-3">No photos found.</div>
	{/if}
	{#each $currentItems as photo}
		<div style="position:relative; padding:.5rem;">
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
		{@const photo = $currentItems[currentPhotoIndex]}
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
</div>
<div style="clear: both;position:fixed;bottom:0;display:flex;" bind:this={footerDiv}>
	<div class="me-3">
		<Pagination last={$lastPage} bind:page />
	</div>
	<div class="me-3">
		<div class="input-group">
			<span class="input-group-text"> Show </span>
			<select name="nmn" value={itemsPerPage} onchange={handleLimitChange} class="form-select">
				<option value={0}>auto</option>
				{#each [10, 20, 50, 100] as val}
					<option>{val}</option>
				{/each}
			</select>
		</div>
	</div>
	{#if selectedPhotos.length}
		<div class="me-3">
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
<DebugPanel value={{ currentPage: $currentPage, photos: $currentItems }} />
