<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { photoStore, photoCriteria } from '$lib/stores/photo-store';
	import Pagination from '$lib/components/Pagination.svelte';
	import Thumbnail from './Thumbnail.svelte';
	import PhotoViewer from './PhotoViewer.svelte';
	import PhotoEditor from './PhotoEditor.svelte';
	import { tick } from 'svelte';
	import Modal from '$lib/components/Modal.svelte';
	import FilterComponent from './FilterComponent.svelte';
	import { pushState, replaceState } from '$app/navigation';
	import { page } from '$app/state';

	let { currentPage, numPerPage, currentItems, totalCount, lastPage } = photoStore;
	let selectedPhotos: number[] = $state([]);
	let pp = $state($currentPage);
	pushState('', { showViewModal: false });
	$effect(() => {
		if (pp !== $currentPage) {
			photoStore.setCurrentPage(pp);
			// pushState(`?page=${pp}`, { pp: pp });
		}
	});
	currentPage.subscribe((C) => {
		if (pp !== C) {
			pp = C;
		}
	});
	// let showViewModal = $state(false);
	function handleThumbnailClick(e: MouseEvent, photo: Photo): void {
		e.preventDefault();
		const x = $currentItems.findIndex((p) => p.id === photo.id);
		pushState(`?show`, { currentItemIndex: x, showViewModal: true });

		//tick().then((_) => viewdialog!.open());
	}

	function handlePrev() {
		console.log('handlePrev');
		const { currentItemIndex } = page.state;
		selectedPhotos = [];
		let prevItemIndex = currentItemIndex == undefined ? 0 : currentItemIndex - 1;
		if (prevItemIndex < 0) {
			if (pp > 1) {
				console.log('prev page');
				pp = pp - 1;
				prevItemIndex = $numPerPage - 1;
			} else {
				// already on first page
				prevItemIndex = 0;
			}
		}
		console.log(`prevItemIndex:${prevItemIndex}`);
		replaceState('?prev', {
			showViewModal: true,
			currentItemIndex: prevItemIndex
		});
	}

	function handleNext() {
		selectedPhotos = [];
		const { currentItemIndex } = page.state;
		let nextItemIndex = currentItemIndex === undefined ? 0 : currentItemIndex + 1;
		if (nextItemIndex >= $currentItems.length) {
			// need a new page
			if (!$lastPage || $lastPage > pp) {
				pp = pp + 1;
				nextItemIndex = 0;
			}
		}
		console.log(`next:${nextItemIndex}`);
		replaceState('?next', {
			showViewModal: true,
			currentItemIndex: nextItemIndex
		});
	}

	function handleLimitChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const x = parseInt(event.currentTarget.value);
		if (x < 1) {
			photoStore.setNumPerPage(autoItems);
		} else {
			photoStore.setNumPerPage(x);
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
			photoStore.setNumPerPage(autoItems);
		}
	});
	let autoItemsTimer: any = 0;
	const thumbWidth = 300;
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
				const itemsPerRow = Math.floor(w / thumbWidth);
				const itemRows = Math.floor(h / thumbWidth);
				autoItems = itemRows * itemsPerRow;
				console.log('autoItems', autoItems);
				if (autoItems < 10) {
					autoItems = 10;
				}
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
<div bind:this={containerDiv} style="display: flex; flex-wrap:wrap; justify-content:space-around;">
	{#if $currentItems.length == 0}
		<div class="alert alert-info m-3">No photos found.</div>
	{/if}
	{#each $currentItems as photo}
		<div class="thumb-container" style="width:{thumbWidth}px">
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
	{#if page.state.showViewModal}
		{@const photo =
			page.state.currentItemIndex === undefined
				? undefined
				: $currentItems[page.state.currentItemIndex]}
		{#if photo}
			<PhotoViewer {photo} onnext={handleNext} onprev={handlePrev} />
		{/if}
	{/if}
</div>
<div style="clear: both;position:fixed;bottom:0;display:flex;" bind:this={footerDiv}>
	{#if selectedPhotos.length}
		<div class="me-3 pb-3">
			<button class="btn btn-primary" onclick={handleEditClick} type="button">
				Edit
				{selectedPhotos.length}
			</button>
			<button class="btn btn-secondary" onclick={() => (selectedPhotos = [])} type="button">
				Deselect
			</button>
		</div>
	{:else}
		<div class="me-3">
			<Pagination last={$lastPage} bind:page={pp} width={5} />
		</div>
		<div class="me-3">
			<div class="input-group">
				<span class="input-group-text d-none d-md-inline"> Show </span>
				<select name="nmn" value={itemsPerPage} onchange={handleLimitChange} class="form-select">
					<option value={0}>auto</option>
					{#each [10, 20, 50, 100] as val}
						<option>{val}</option>
					{/each}
				</select>
			</div>
		</div>
	{/if}
</div>

<Modal bind:this={editDialog} closedBy="closerequest">
	{#snippet title()}
		Edit {photosToEdit.length} Item{photosToEdit.length == 1 ? '' : 's'}
	{/snippet}
	<PhotoEditor photos={photosToEdit} onsave={handleOnSave} oncancel={() => editDialog?.close()} />
</Modal>
<DebugPanel value={{ state: page.state, currentPage: $currentPage, photos: $currentItems }} />
<style>
	.thumb-container {
		position:relative; 
		padding:5px;
	}
</style>