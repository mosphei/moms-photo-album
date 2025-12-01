<script lang="ts">
	import type { Photo } from '$lib/models/photo';
	import { photoPath } from '$lib/stores/photo-store';
	interface IProps {
		photo: Photo;
		onclick?: (e: MouseEvent) => void;
	}
	let { photo, onclick = undefined }: IProps = $props();
	let img: HTMLImageElement;

	function handleClick(event: MouseEvent & { currentTarget: EventTarget & HTMLAnchorElement }) {
		throw new Error('Function not implemented.');
	}
</script>

<a class="card" href={photo.filename} {onclick}>
	<img class="card-img-top" bind:this={img} alt={photo.filename} src={photoPath('t', photo)} />
	<div class="card-body">
		{photo.date_taken.toLocaleDateString()}
		{photo.description}
	</div>
</a>

<style>
	.card {
		width: 12rem;
		height: 12rem;
		border: solid 1px;
		margin: 1rem;
		float: left;
		text-decoration: none;
	}
	.card:hover {
		border-color: var(--mo-primary);
		color: var(--mo-primary);
	}
	img {
		width: 12rem;
		height: 8rem;
		object-fit: cover;
		object-position: top;
	}
</style>
