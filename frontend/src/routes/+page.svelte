<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { getPhotos, photoPath } from '$lib/stores/photo-store';
	import { onMount, tick } from 'svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import Thumbnail from './Thumbnail.svelte';
	import { clickOutside } from '$lib/click-outside';

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
		selectedPhotoIndex = photos.findIndex(p=>p.id === photo.id);
		dialog.showModal();
	}
</script>

{#each photos as photo}
	<Thumbnail {photo} onclick={e=>handleThumbnailClick(e,photo)}/>
{/each}
<dialog bind:this={dialog} >
	{#if selectedPhotoIndex >= 0}
	{@const photo = photos[selectedPhotoIndex]}
	<div class="modal-dialog" use:clickOutside={(e)=>dialog.close()}>
		<div class="modal-header">
			<h5 class="modal-title">
				{photo.date_taken.toLocaleDateString()}
				{photo.file_path}
			</h5>
			<button type="button" class="btn-close" aria-label="Close"></button>
		</div>
		<div class="modal-body mb-2">
			<img src={photoPath("m", photo.id)} alt={photo.file_path} >
		</div>
		<div class="modal-footer">
			<button class="btn btn-primary">Prev</button>
			<span style="flex:1"></span>
			<button class="btn btn-primary">Next</button>
		
		</div>
	</div>
	
	{/if}
</dialog>
<div style="position:sticky; bottom:.25rem; clear: both;">
	<Pagination {last} bind:page />
</div>
<DebugPanel value={photos} />
<style>
	/* Styles for the dialog itself (optional) */
dialog {
  border: none;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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