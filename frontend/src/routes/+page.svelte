<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { Photo } from '$lib/models/photo';
	import { getPhotos } from '$lib/stores/photo-store';
	import { onMount } from 'svelte';
	import PhotoElement from './PhotoElement.svelte';
	let pics:Photo[] = $state([]);
	$effect(()=>{

	})
	onMount(()=>{
		getPhotos(0, 5)
		.then(p=>pics = p);
	});
</script>
{#each pics as photo}
	<div>
		<PhotoElement {photo} />
	</div>
{/each}
<div style="position:sticky; bottom:.25rem">
	<ul class="pagination">
		<li class="page-item"><a href="#" class="page-link">First</a></li>
		<li class="page-item"><a href="#" class="page-link">Previous</a></li>
		<li class="page-item"><a class="page-link" href="#">1</a></li>
		<li class="page-item active">
		<a class="page-link" href="#" aria-current="page">2</a>
		</li>
		<li class="page-item"><a class="page-link" href="#">3</a></li>
		<li class="page-item"><a class="page-link" href="#">Next</a></li>
		<li class="page-item"><a class="page-link" href="#">Last</a></li>
	</ul>
</div>