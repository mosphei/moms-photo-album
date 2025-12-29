<script lang="ts">
	import PageTitle from '$lib/components/PageTitle.svelte';
	import { onMount, tick } from 'svelte';
	import type { PageProps } from './$types';
	import { fetchApi } from '$lib/stores/common-store';
	import { dateTimeReviver, shuffleInPlace } from '$lib/utils';
	import type { Slideshow } from '$lib/models/slideshow';
	import { photoPath, type Photo } from '$lib/models/photo';
	import ModalContent from '$lib/components/modal/ModalContent.svelte';
	import ModalBody from '$lib/components/modal/ModalBody.svelte';
	import { page } from '$app/state';
	import { onNavigate, pushState } from '$app/navigation';
	import ModalDialog from '$lib/components/modal/ModalDialog.svelte';
	import { fade } from 'svelte/transition';
	import Pagination from '$lib/components/Pagination.svelte';
	import { PaginatedStore } from '$lib/models/paginated-store';
	import { errorAlert, progressAlert } from '$lib/alerts';
	import { saveSlideshow } from '$lib/stores/slideshow-store';

	let { data }: PageProps = $props();
	let contentRef: HTMLDivElement | undefined = $state();
	$inspect(data);
	let title = $state(`${data.id}`);
	let slideshow: Slideshow | undefined = $state();

	let duration = $state(5000);

	page.state.showViewModal = false;
	page.state.currentItemIndex = 0;
	function play() {
		pushState('', { showViewModal: true });
		tick().then(() => {
			contentRef?.requestFullscreen();
		});
	}

	const slideStore = new PaginatedStore<Photo>(async (x: number, y: number, z: any) => {
		const url = `/api/slideshows/${data.id}/slides`;
		const response = await fetchApi(url, { headers: { accept: 'application/json' } });
		let photos: Photo[] = [];
		if (response) {
			photos = JSON.parse(response, dateTimeReviver);
		}
		return {
			offset: 0,
			limit: photos.length,
			items: photos,
			total_count: photos.length
		};
	});
	let { currentItems, currentPage, totalCount, lastPage, numPerPage } = slideStore;
	let pp = $state($currentPage);
	// synch pp and currentPage;
	$effect(() => {
		slideStore.setCurrentPage(pp);
	});
	currentPage.subscribe((p) => (pp = p));

	let playList: number[] = $state([]);
	let shuffle = $state(true);
	$effect(() => {
		if ($totalCount) {
			let slideIndices = Array.from({ length: $totalCount }).map((v, i) => i);
			if (shuffle) {
				shuffleInPlace(slideIndices);
			}
			playList = slideIndices;
		}
	});
	let currentIdx = $state(0);

	async function nextItem() {
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
		const nextPhoto = await slideStore.getItem(playList[nextIdx]);
		if (nextPhoto) {
			fetch(photoPath('l', nextPhoto));
		}
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
		slideStore.setCurrentPage(1);
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
		slideIndex: number
	) {
		event.preventDefault();
		// might be shuffled?
		const idx = playList.findIndex((s) => s == slideIndex);
		if (idx >= 0) {
			currentIdx = idx;
			play();
		}
	}
	let selectedSlideIds: number[] = $state([]);
	function handleSelectSlide(
		event: MouseEvent & { currentTarget: EventTarget & HTMLInputElement }
	) {
		if (event.shiftKey) {
			if (selectedSlideIds.length > 0) {
				const last_chosen = selectedSlideIds[selectedSlideIds.length - 1];
				const idx = $currentItems.findIndex((p) => p.id === last_chosen);
				const currentId = parseInt(event.currentTarget.value);
				const currentIdx = $currentItems.findIndex((p) => p.id === currentId);
				const [first, last] = currentIdx > idx ? [idx, currentIdx] : [currentIdx, idx];
				selectedSlideIds = Array.from(
					new Set([
						...selectedSlideIds,
						...$currentItems.filter((itm, i) => i >= first && i <= last).map((itm) => itm.id)
					])
				);
			}
		}
	}
	async function handleRemoveSlides(
		event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }
	) {
		const msg = progressAlert('saving...');
		try {
			const oldSlideList: Photo[] = await slideStore.allItems();
			const newSlideList = oldSlideList
				.map((p) => p.id)
				.filter((id) => !selectedSlideIds.includes(id));
			if (!slideshow?.id) {
				throw new Error('unable to get slideshow id');
			}
			if (!slideshow?.title) {
				throw new Error('unable to get slideshow title');
			}
			await saveSlideshow({
				id: slideshow.id,
				title: slideshow.title,
				slides: newSlideList
			});
			slideStore.refresh();
		} catch (error) {
			errorAlert('unable to save slideshow', error, 1500);
		} finally {
			msg.dismiss();
		}
	}

	onMount(async () => {
		const msg = progressAlert('loading slides...');
		try {
			slideStore.refresh();
		} catch (error) {
			errorAlert('unable to load slides!', error, 15000);
		} finally {
			msg.dismiss();
		}
	});
</script>

<svelte:window onkeydown={handleKeydown} />
<PageTitle {title}>
	<div class="d-flex">
		<h1>
			Slideshow {title}
		</h1>
		<div style="flex:1"></div>
		<div class="d-flex gap-2 small" style="height: auto;">
			<button onclick={play} type="button" class="btn btn-outline-primary"> Play </button>
			<div class="form-check form-switch">
				<input
					class="form-check-input"
					type="checkbox"
					role="switch"
					id="switchShuffle"
					bind:checked={shuffle}
				/>
				<label class="form-check-label" for="switchShuffle">Shuffle</label>
			</div>
		</div>
	</div>
</PageTitle>

<div class="d-flex flex-wrap justify-space-around">
	{#snippet thumbnail(photo: Photo, idx: number)}
		<div class="thumb-container">
			<a class="card" href={photoPath('l', photo)} onclick={(e) => handleThumbClick(e, idx)}>
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
			<label style="position:absolute;top:0;left:0;padding:1rem" for="select_{photo.id}">
				<input
					type="checkbox"
					id="select_{photo.id}"
					bind:group={selectedSlideIds}
					value={photo.id}
					onclick={handleSelectSlide}
				/>
			</label>
		</div>
	{/snippet}
	{#each $currentItems as slide, idx (slide.id)}
		{@render thumbnail(slide, idx)}
	{/each}
</div>
<div>
	<Pagination bind:page={pp} last={$lastPage} />
</div>
{#if page.state.showViewModal}
	<ModalDialog --background="black">
		<ModalContent bind:contentRef>
			<ModalBody>
				{#each [playList[currentIdx]] as slideIndex (currentIdx)}
					{#await slideStore.getItem(slideIndex)}
						<div>loading...</div>
					{:then photo}
						{#if photo}
							<div style="width:100%" transition:fade={{ duration: 300 }}>
								<div style="width:100%;position:relative;">
									{#if photo.content_type?.startsWith('video')}
										<!-- svelte-ignore a11y_media_has_caption -->
										<video controls poster={photoPath('m', photo)} width="100%" autoplay>
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
						{/if}
					{/await}
				{/each}
			</ModalBody>
		</ModalContent>
	</ModalDialog>
{/if}
{#if selectedSlideIds.length}
	<div id="action-buttons">
		<button class="btn btn-primary" onclick={handleRemoveSlides}>
			Remove {selectedSlideIds.length}
		</button>
		<button class="btn btn-secondary" onclick={() => (selectedSlideIds = [])}> Deselect </button>
	</div>
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
