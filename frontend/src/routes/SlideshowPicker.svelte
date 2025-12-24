<script lang="ts">
	import { errorAlert, progressAlert } from '$lib/alerts';
	import ModalBody from '$lib/components/modal/ModalBody.svelte';
	import ModalContent from '$lib/components/modal/ModalContent.svelte';
	import ModalFooter from '$lib/components/modal/ModalFooter.svelte';
	import ModalTitle from '$lib/components/modal/ModalTitle.svelte';
	import { photoPath, type Photo } from '$lib/models/photo';
	import type { Slideshow } from '$lib/models/slideshow';
	import { saveSlideshow, slideshowStore } from '$lib/stores/slideshow-store';
	interface IProps {
		photos: Photo[];
		onclose: () => void;
	}
	let { photos, onclose }: IProps = $props();
	let { currentItems } = slideshowStore;
	let selectedSlideshow: Slideshow | undefined = $state();
	let searchText = $state('');

	function handleSelect(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		throw new Error('Function not implemented.');
	}

	function handleAddNew(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		selectedSlideshow = {
			id: 0,
			title: searchText,
			length: 0,
			slides: photos
		};
	}

	function handleCancel(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		onclose?.();
	}

	async function handleAppend(
		event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }
	) {
		const msg = progressAlert('updating slideshow');
		try {
			if (!selectedSlideshow) {
				throw new Error('please select a slideshow');
			}
			const photo_ids = Array.from(
				new Set([...selectedSlideshow!.slides, ...photos].map((p) => p.id))
			);

			await saveSlideshow({
				id: selectedSlideshow.id,
				title: selectedSlideshow.title,
				slides: photo_ids
			});

			onclose?.();
		} catch (error) {
			errorAlert('unable to save slideshow!', error, 15000);
		} finally {
			msg.dismiss();
		}
	}

	async function handleAppendAndSort(
		event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }
	) {
		const msg = progressAlert('updating slideshow');
		try {
			if (!selectedSlideshow) {
				throw new Error('please select a slideshow');
			}
			const photo_ids = new Set(
				[...selectedSlideshow.slides, ...photos]
					.toSorted((a: Photo, b: Photo) => {
						if (a.date_taken < b.date_taken) {
							return -1;
						}
						if (a.date_taken < b.date_taken) {
							return 1;
						}
						return a.id - b.id;
					})
					.map((p) => p.id)
			);
			await saveSlideshow({
				id: selectedSlideshow.id,
				title: selectedSlideshow.title,
				slides: Array.from(photo_ids)
			});
			onclose?.();
		} catch (error) {
			errorAlert('unable to save slideshow!', error, 15000);
		} finally {
			msg.dismiss();
		}
	}
</script>

<ModalContent>
	<ModalTitle onCloseButton={() => onclose()}>
		Add {photos.length} Item{photos.length == 1 ? '' : 's'} to Slideshow
	</ModalTitle>
	<ModalBody>
		<div class="d-flex flex-wrap mb-2" style="width: 100%;">
			{#each photos as photo}
				<div style="margin:4px; width: 200px; height:200px">
					<img
						src={photoPath('t', photo)}
						alt={photo.filename}
						style="object-fit: contain;width:100%;height:100%;transform:rotate(var(--rotation,0));transform-origin:center center"
					/>
				</div>
			{/each}
		</div>
		{#if selectedSlideshow}
			<div class="mb-3">
				<strong>{selectedSlideshow.title}</strong>
				<div>
					current length:
					{selectedSlideshow.length}
				</div>
			</div>
		{:else}
			<div>
				<input class="form-control" bind:value={searchText} />
			</div>
			<div class="mb-3 list-group">
				{#if $currentItems.length < 1}
					<div class="list-group-item">No items found</div>
				{/if}
				{#each $currentItems as slideshow}
					<div class="list-group-item">
						<button class="btn btn-outline-primary" onclick={handleSelect}> Select </button>
						{slideshow.title}
					</div>
				{/each}
				{#if searchText}
					<div class="list-group-item">
						<button class="btn btn-outline-primary" type="button" onclick={handleAddNew}>
							New Slideshow "{searchText}"
						</button>
					</div>
				{/if}
			</div>
		{/if}
	</ModalBody>
	<ModalFooter>
		<button class="btn btn-primary me-3" type="button" onclick={handleAppend}>
			Append to slideshow
		</button>
		<button class="btn btn-primary me-3" type="button" onclick={handleAppendAndSort}>
			Add to slides in Date Order
		</button>
		<button class="btn btn-secondary" onclick={handleCancel} type="button"> Cancel </button>
	</ModalFooter>
</ModalContent>
