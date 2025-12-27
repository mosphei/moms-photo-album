<script lang="ts">
	import PageTitle from '$lib/components/PageTitle.svelte';
	import { onMount, tick } from 'svelte';
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
	let contentRef: HTMLDivElement | undefined = $state();
	$inspect(data);
	let title = $state(`${data.id}`);
	let slideshow: Slideshow | undefined = $state();
	let slides: Photo[] = $state([]);
	let duration = $state(5000);

	page.state.showViewModal = false;
	page.state.currentItemIndex = 0;
	function play() {
		pushState('', { showViewModal: true });
		tick().then(() => {
			contentRef?.requestFullscreen();
		});
	}

	async function getSlides(id: number) {
		const url = `/api/slideshows/${data.id}/slides`;
		const response = await fetchApi(url, { headers: { accept: 'application/json' } });
		if (response) {
			slides = JSON.parse(response, dateTimeReviver);
		}
	}
	let playList: Photo[] = $state([]);
	let shuffle = $state(false);
	$effect(() => {
		if (slides.length) {
			let slideIndices = Array.from({ length: slides.length }).map((v, i) => i);
			if (shuffle) {
				slideIndices = slideIndices.toSorted((a, b) => Math.random() - 0.5);
			}
			playList = slideIndices.map((i) => slides[i]);
		}
	});
	let currentIdx = $state(0);

	function nextItem() {
		console.log('nextItem', page.state.showViewModal);
		if (!page.state.showViewModal) {
			stopTimer();
		}
		if (currentIdx >= playList.length - 1) {
			currentIdx = 0;
		} else {
			currentIdx = currentIdx + 1;
		}
		const nextIdx = currentIdx + 1;

		// cache the next img
		fetch(photoPath('l', playList[nextIdx]));
	}
	function prevItem() {
		if (currentIdx <= 0) {
			currentIdx = playList.length - 1;
		} else {
			currentIdx = currentIdx - 1;
		}
	}

	let intervalTimerId: any;
	function startTimer() {
		if (intervalTimerId) {
			clearInterval(intervalTimerId);
		}
		console.log('startTimer');
		intervalTimerId = setInterval(() => {
			if (page.state.showViewModal) {
				nextItem();
			} else {
				stopTimer();
			}
		}, duration);
	}
	function stopTimer() {
		console.log('stopTimer');
		clearInterval(intervalTimerId);
	}
	$effect(() => {
		console.log('page.state.showViewModal', page.state.showViewModal);
		if (page.state.showViewModal) {
			startTimer();
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

	function handleKeydown(event: KeyboardEvent & { currentTarget: EventTarget & Window }) {
		console.log(`Key pressed: ${event.key}`);
		if (event.key == 'ArrowLeft') {
			event.preventDefault();
			prevItem();
			startTimer();
		} else if (event.key == 'ArrowRight') {
			event.preventDefault();
			nextItem();
			startTimer();
		}
	}

	function handleThumbClick(
		event: MouseEvent & { currentTarget: EventTarget & HTMLAnchorElement },
		photo: Photo
	) {
		event.preventDefault();
		const idx = playList.findIndex((s) => s.id == photo.id);
		if (idx >= 0) {
			currentIdx = idx;
			play();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />
<PageTitle {title}>
	<h1>
		Slideshow {title}
		<small
			><button onclick={play} type="button" class="btn btn-outline-primary"> Play </button></small
		>
	</h1>
</PageTitle>

<div class="d-flex flex-wrap justify-space-around">
	{#snippet thumbnail(photo: Photo)}
		<div class="thumb-container">
			<a class="card" href={photoPath('l', photo)} onclick={(e) => handleThumbClick(e, photo)}>
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
	{#each slides as slide (slide.id)}
		{@render thumbnail(slide)}
	{/each}
</div>
{#if page.state.showViewModal}
	<ModalDialog --background="black">
		<ModalContent bind:contentRef>
			<ModalBody>
				{#each [playList[currentIdx]] as photo (currentIdx)}
					<div style="width:100%" transition:fade={{ duration: 300 }}>
						<div style="width:100%;position:relative;">
							{#if photo.content_type?.startsWith('video')}
								<!-- svelte-ignore a11y_media_has_caption -->
								<video controls poster={photoPath('m', photo)} width="100%">
									<source src={photoPath('o', photo)} type={photo.content_type} />
								</video>
							{:else}
								<img
									src={photoPath('m', photo)}
									alt={photo.filename}
									style="object-fit:contain;object-position:center;width:100%;max-height: 100vh;"
								/>
							{/if}
							<div class="left">
								<button aria-label="Previous" type="button" onclick={prevItem}>
									<span></span>
								</button>
							</div>
							<div class="right">
								<button aria-label="Next" type="button" onclick={nextItem}>
									<span></span>
								</button>
							</div>
						</div>
						<div>
							{photo.description}
						</div>
					</div>
				{/each}
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
	/* next, prev buttons */
	.left,
	.right {
		position: absolute;
		top: 0;
		bottom: 2rem;
		z-index: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 15%;
		padding: 0;
		color: #fff;
		text-align: center;
	}
	.left {
		left: 0;
	}
	.right {
		right: 0;
	}
	.left button:hover,
	.right button:hover {
		color: var(--mo-primary);
		opacity: 1;
	}
	.left span,
	.right span {
		display: inline-block;
		width: 2rem;
		height: 2rem;
		background-repeat: no-repeat;
		background-position: 50%;
		background-size: 100% 100%;
	}
	.right span {
		background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23fff'%3e%3cpath d='M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
	}
	.left span {
		background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23fff'%3e%3cpath d='M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z'/%3e%3c/svg%3e");
	}
	.left button,
	.right button {
		border: none;
		background: transparent;
		padding: 1rem;
		background: 0 0;
		border: 0;
		opacity: 0.5;
		transition: opacity 0.15s ease;
	}
</style>
