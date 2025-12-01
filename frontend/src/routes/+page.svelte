<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { getPhotos, photoPath } from '$lib/stores/photo-store';
	import { onMount, tick } from 'svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import Thumbnail from './Thumbnail.svelte';

	let dialog: HTMLDialogElement;
	let photos: Photo[] = $state([]);
	let page = $state(1);
	let limit = $state(5);
	let total = $state(-1);
	let last: number | undefined = $state(undefined);
	let selectedPhotoIndex = $state(-1);

	async function loadPhotos() {
		const results = await getPhotos(page, limit);
		photos = results.items;
		total = results.total_count;
		if (total) {
			last = Math.ceil(total / limit);
		}
	}

	$effect(() => {
		console.log(`page=${page}`);
		loadPhotos();
	});

	onMount(() => {
		loadPhotos();
	});

	function handleThumbnailClick(e: MouseEvent, photo: Photo): void {
		e.preventDefault();
		selectedPhotoIndex = photos.findIndex((p) => p.id === photo.id);
		dialog.showModal();
	}

	function handlePrev(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		console.log('handlePrev');
		event.preventDefault();
		if (selectedPhotoIndex < 1) {
			if (page > 1) {
				page = page - 1;
				selectedPhotoIndex = photos.length - 1;
			} else {
				selectedPhotoIndex = 0;
			}
		} else {
			selectedPhotoIndex = selectedPhotoIndex - 1;
		}
	}

	function handleNext(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		if (selectedPhotoIndex >= photos.length - 1) {
			page = page + 1;
			selectedPhotoIndex = 0;
		} else {
			selectedPhotoIndex = selectedPhotoIndex + 1;
		}
	}
</script>

{#each photos as photo}
	<Thumbnail {photo} onclick={(e) => handleThumbnailClick(e, photo)} />
{/each}
<dialog bind:this={dialog} closedby="any">
	{#if selectedPhotoIndex >= 0}
		{@const photo = photos[selectedPhotoIndex]}
		<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">
					{photo.date_taken.toLocaleDateString()}
					{photo.filename}
				</h5>
				<button class="btn-close" aria-label="Close" onclick={() => dialog.close()}></button>
			</div>
			<div class="modal-body mb-2 d-flex justify-content-center">
				<div style="width:100%;height:100%">
					<img
						src={photoPath('m', photo)}
						alt={photo.filename}
						style="object-fit: contain;object-position:center;width:100%;height:100%"
					/>
				</div>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-primary" onclick={handlePrev}>Prev</button>
				<span style="flex:1"></span>
				<button type="button" class="btn btn-primary" onclick={handleNext}>Next</button>
			</div>
		</div>
	{/if}
</dialog>
<div style="position:sticky; bottom:.25rem; clear: both;">
	<Pagination {last} bind:page />
</div>
<DebugPanel value={photos} />

<style>
	dialog {
		width: 80%;
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
		/* Change the background color from the default low-opacity black */
		background-color: rgba(0, 0, 100, 0.7);

		/* Use gradients, images, etc. */
		/* background-image: linear-gradient(45deg, magenta, dodgerblue); */

		/* You can also add blur effects to the content behind the dialog */
		/* Note: Browser support for backdrop-filter is good, but check if needed */
		backdrop-filter: blur(5px);

		/* Add transitions/animations */
		/* transition: background-color 0.3s ease-in-out; */
	}
</style>
