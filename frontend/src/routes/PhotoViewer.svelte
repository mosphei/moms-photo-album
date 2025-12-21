<script lang="ts">
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import { photoPath, type Photo } from '$lib/models/photo';
	import { IMAGESIZES, type SizeEnum } from '$lib/models/settings';
	import { onMount } from 'svelte';

	interface iProps {
		size?: SizeEnum;
		photo: Photo;
		onprev: () => void;
		onnext: () => void;
	}
	let { size = undefined, photo, onnext, onprev }: iProps = $props();
	const imgSize = size ? size : 'm';
	let [width, height] = IMAGESIZES[imgSize];
	let dialog: HTMLDialogElement;

	function handleClose(event: Event & { currentTarget: EventTarget & HTMLDialogElement }) {
		event.preventDefault();
		history.back();
	}
	onMount(() => {
		dialog.showModal();
	});
</script>

<dialog closedby="any" onclose={handleClose} bind:this={dialog}>
	<div>
		{photo.date_taken.toDateString()}
	</div>
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
			<button aria-label="Previous" type="button" onclick={onprev}>
				<span></span>
			</button>
		</div>
		<div class="right">
			<button aria-label="Next" type="button" onclick={onnext}>
				<span></span>
			</button>
		</div>
	</div>
	<div>
		{photo.description}
	</div>
	<DebugPanel value={{ photo }} />
</dialog>

<style>
	dialog {
		width: 90%;
		border-radius: 6px;
		padding: 0.5rem;
		--mo-modal-header-border-color: var(--mo-primary);
		--mo-modal-header-border-width: 1px;
		--mo-heading-color: var(--mo-primary);
		--mo-modal-header-padding: 0.25rem;
		--mo-modal-padding: 0.25rem;
		background-color: black;
		color: white;
	}

	/* Styles for the backdrop */
	dialog::backdrop {
		background-color: rgba(0, 0, 100, 0.7);
		backdrop-filter: blur(3px);
	}
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
	button {
		border: none;
		background: transparent;
		padding: 1rem;
		background: 0 0;
		border: 0;
		opacity: 0.5;
		transition: opacity 0.15s ease;
	}
</style>
