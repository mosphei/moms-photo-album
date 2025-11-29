<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { getPhotos } from '$lib/stores/photo-store';
	import { onMount } from 'svelte';
	import PhotoElement from './PhotoElement.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	let photos: Photo[] = $state([]);
	let page = $state(1);
	let limit = $state(5);
	let total = $state(-1);
	let last: number | undefined = $state(undefined);

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
</script>

{#each photos as photo}
	<PhotoElement {photo} />
{/each}
<div style="position:sticky; bottom:.25rem; clear: both;">
	<Pagination {last} bind:page />
</div>
<DebugPanel value={photos} />
