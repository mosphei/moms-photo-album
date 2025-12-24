<script lang="ts">
	import PageTitle from '$lib/components/PageTitle.svelte';
	import { onMount } from 'svelte';
	import type { PageProps } from './$types';
	import { fetchApi } from '$lib/stores/common-store';
	import { dateTimeReviver } from '$lib/utils';
	import type { Slideshow } from '$lib/models/slideshow';
	import { photoPath, type Photo } from '$lib/models/photo';
	import ModalContent from '$lib/components/modal/ModalContent.svelte';
	import ModalBody from '$lib/components/modal/ModalBody.svelte';
	import { page } from '$app/state';
	import { onNavigate, pushState } from '$app/navigation';
	import ModalDialog from '$lib/components/modal/ModalDialog.svelte';
	import { fade } from 'svelte/transition';

	let { data }: PageProps = $props();
	$inspect(data);
	let title = $state(`${data.id}`);
	let slideshow: Slideshow | undefined = $state();
	let slides: Photo[] = $state([]);
	let duration = $state(5000);

	page.state.showViewModal = false;
	page.state.currentItemIndex = 0;
	function play() {
		pushState('', { showViewModal: true });
	}

	async function getSlides(id: number) {
		const url = `/api/slideshows/${data.id}/slides`;
		const response = await fetchApi(url, { headers: { accept: 'application/json' } });
		if (response) {
			slides = JSON.parse(response, dateTimeReviver);
		}
	}
	let shuffle = $state(false);
	let currentIdx = $state(0);
	let nextIdx = $state(1);

	function nextItem() {
		console.log('nextItem');
		currentIdx = nextIdx;
		if (shuffle) {
			nextIdx = Math.floor(Math.random() * slides.length);
		} else {
			nextIdx = currentIdx + 1;
		}
		// cache the next img
		fetch(photoPath('l', slides[nextIdx]));
	}
	let intervalTimerId: any;
	$effect(() => {
		if (page.state.showViewModal) {
			if (intervalTimerId) {
				clearInterval(intervalTimerId);
			}
			intervalTimerId = setInterval(() => {
				if (page.state.showViewModal) {
					nextItem();
				}
			}, duration);
		} else {
			if (intervalTimerId) {
				clearInterval(intervalTimerId);
			}
		}
		return () => clearInterval(intervalTimerId);
	});

	onMount(async () => {
		const url = `/api/slideshows/${data.id}`;
		const response = await fetchApi(url, { headers: { accept: 'application/json' } });
		console.log(url, response);
		if (response) {
			const result: Slideshow = JSON.parse(response, dateTimeReviver);
			slideshow = result;
			title = result.title;
		}
		getSlides(data.id);
	});
</script>

<PageTitle {title}>
	<h1>Slideshow {title}</h1>
	<small><button onclick={play}> Play </button></small>
</PageTitle>

<div class="d-flex flex-wrap justify-space-around">
	{#snippet thumbnail(photo: Photo)}
		<div class="thumb-container">
			<a class="card" href={photoPath('l', photo)}>
				<img alt={photo.filename} src={photoPath('t', photo)} />
				<section>
					<div>
						{photo.date_taken.toLocaleDateString()}
					</div>
					{#if photo.description}
						<div>{photo.description}</div>
					{/if}
				</section>
			</a>
		</div>
	{/snippet}
	{#each slides as slide}
		{@render thumbnail(slide)}
	{/each}
</div>
{#if page.state.showViewModal}
	<ModalDialog --background="black">
		<ModalContent>
			<ModalBody>
				{#each [slides[currentIdx]] as slide (currentIdx)}
					<div style="width:100%" transition:fade={{ duration: 300 }}>
						<img src={photoPath('l', slide)} alt={slide.filename} />
					</div>
				{/each}

				<button onclick={nextItem} type="button">Next</button>
			</ModalBody>
		</ModalContent>
	</ModalDialog>
{/if}

<style>
	.thumb-container {
		position: relative;
		padding: 5px;
		width: 300px;
	}
	a {
		width: 100%;
		height: 100%;
		border: solid 1px;
		/*margin: 1rem;
		float: left;*/
		text-decoration: none;
		overflow: hidden;
	}
	a:hover {
		border-color: var(--mo-primary);
		color: var(--mo-primary);
	}
	img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		object-position: top;
	}
	section {
		position: absolute;
		bottom: 0px;
		width: 100%;
		background-color: #fff;
	}
</style>
