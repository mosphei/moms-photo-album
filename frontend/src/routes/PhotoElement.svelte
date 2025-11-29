<script lang="ts">
	import type { Photo } from '$lib/models/photo';
	import { fetchApi } from '$lib/stores/common-store';
	import { session } from '$lib/stores/session-store';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';

	let { photo }: { photo: Photo } = $props();
	const parts = photo.file_path.split('/');
	const filename = parts.pop();
	let img: HTMLImageElement;
	onMount(() => {
		const token = get(session.token);
		fetch(`/api/images/files/thumb/${photo.id}/${filename}`, {
			headers: {
				Authorization: token ? `${token.token_type} ${token.access_token}` : 'undefined'
			}
		})
			.then((response) => response.blob())
			.then((blob) => {
				img.src = URL.createObjectURL(blob);
			});
	});
</script>

<a class="card" href="/blah/blah">
	<img class="card-img-top" bind:this={img} alt={filename} />
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
	}
</style>
