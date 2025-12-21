<script lang="ts">
	import { photoPath, type Photo } from '$lib/models/photo';
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

<a class="card" href={photoPath('l', photo)} {onclick}>
	<img bind:this={img} alt={photo.filename} src={photoPath('t', photo)} />
	<section>
		<div>
			{photo.date_taken.toLocaleDateString()}
		</div>
		{#if photo.description}
			<div>{photo.description}</div>
		{/if}
	</section>
</a>

<style>
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
