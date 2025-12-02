<script lang="ts">
	import type { Photo } from '$lib/models/photo';
	import Thumbnail from './Thumbnail.svelte';

	interface IProps {
		photos: Photo[];
		onsave?: () => void;
		oncancel?: () => void;
	}
	let { photos, onsave, oncancel }: IProps = $props();

	function handleCancel(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		if (oncancel) oncancel();
	}

	function save(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		if (onsave) onsave();
		throw new Error('Function not implemented.');
	}
</script>

<div class="row g-1 mb-2">
	{#each photos as photo}
		<div class="col-auto"><Thumbnail {photo} /></div>
	{/each}
</div>
<div class="d-flex justify-content-between">
	<button class="btn btn-primary" onclick={save}>Save</button>
	<button class="btn btn-secondary" type="button" onclick={handleCancel}>Cancel</button>
</div>
