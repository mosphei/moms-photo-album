<script lang="ts">
	import { getPhotos } from '$lib/stores/photo-store';
	import { getPeople } from '$lib/stores/people-store';
	import { onMount } from 'svelte';
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import type { Person } from '$lib/models/person';
	import { page } from '$app/stores';
	const limit = 100;

	let q = $state($page.url.searchParams.get('q'));
	let allPhotos: Photo[] = $state([]);
	let allPeople: Person[] = $state([]);

	let phototime = $state(0);
	let persontime = $state(0);

	async function loadAllPhotos() {
		let start = performance.now();
		let currentPage = 1;
		let lastPage = 2;
		while (currentPage <= lastPage) {
			const result = await getPhotos(currentPage, limit);
			if (result) {
				if (result.total_count) {
					lastPage = Math.ceil(result.total_count / limit);
				}
				if (result.items.length) {
					allPhotos = [...allPhotos, ...result.items];
				} else {
					break;
				}
			}
			currentPage = currentPage + 1;
		}
		phototime = performance.now() - start;
	}
	async function loadAllPeople() {
		let start = performance.now();
		let currentPage = 1;
		let lastPage = 2;
		while (currentPage <= lastPage) {
			const result = await getPeople(currentPage, limit);
			if (result) {
				if (result.total_count) {
					lastPage = Math.ceil(result.total_count / limit);
				}
				if (result.items.length) {
					allPeople = [...allPeople, ...result.items];
				} else {
					break;
				}
			}
			currentPage = currentPage + 1;
		}
		persontime = performance.now() - start;
	}
	onMount(async () => {
		loadAllPeople();
		loadAllPhotos();
	});
</script>

<svelte:head><title>PhotoDB - Search</title></svelte:head>

<DebugPanel
	value={{
		q,
		phototime,
		persontime,
		lengths: { people: allPeople.length, photos: allPhotos.length }
	}}
/>
