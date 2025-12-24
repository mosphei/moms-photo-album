<script lang="ts">
	import { resolve } from '$app/paths';
	import { errorAlert } from '$lib/alerts';
	import PageTitle from '$lib/components/PageTitle.svelte';
	import { PaginatedStore } from '$lib/models/paginated-store';
	import type { Slideshow } from '$lib/models/slideshow';
	import { slideshowStore } from '$lib/stores/slideshow-store';
	import { onMount } from 'svelte';
	import { slide } from 'svelte/transition';

	let { currentPage, lastPage, numPerPage, totalCount, currentItems } = slideshowStore;
	onMount(async () => {
		try {
			await slideshowStore.setCurrentPage(1);
		} catch (error) {
			errorAlert('unable to get slideshows', error, 15000);
		}
	});

	let showAddform = $state(false);
	function handleAddNew(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
		throw new Error('Function not implemented.');
	}
</script>

<PageTitle title="Slideshows">
	<h1>Slideshows</h1>
</PageTitle>
{#if $currentItems.length}
	{@const startIndex = ($currentPage - 1) * $numPerPage + 1}
	<div>
		{startIndex}
		to {startIndex + $currentItems.length}
		of {$totalCount}
	</div>
{/if}

{#snippet viewSlideshowListItem(slideshow: Slideshow)}
	<div class="list-group-item">
		<div class="d-flex w-100">
			<h5 class="mb-1">
				{slideshow.title}
			</h5>
			<span style="flex:1"></span>

			<a
				class="btn btn-secondary"
				href={resolve('/slideshows/[slug]', { slug: slideshow.id.toString() })}
				title="Edit"
			>
				<span class="bi bi-pencil"></span>
				Edit
			</a>
		</div>

		<p class="mb-1">
			{slideshow.slides.length}
			slide{slideshow.slides.length === 1 ? '' : 's'}
		</p>
	</div>
{/snippet}

<div class="list-group">
	{#if $totalCount !== undefined && $totalCount < 1}
		<div class="list-group-item">No items found.</div>
	{/if}
	{#each $currentItems as slideshow}
		<div class="list-group-item"></div>
	{/each}
	<!-- add slideshow form -->
	{#if showAddform}
		<form
			class="list-group-item"
			action="/api/slideshows/new"
			method="POST"
			onsubmit={handleAddNew}
			transition:slide
		>
			<div class="mb-3">
				<label for="title">Title:</label>
				<input name="title" id="title" class="form-control" required />
			</div>
			<div class="d-flex">
				<button class="btn btn-primary me-3">Add</button>
				<button class="btn btn-secondary" type="reset" onclick={() => (showAddform = false)}>
					Cancel
				</button>
			</div>
		</form>
	{:else}
		<div class="list-group-item">
			<button class="btn btn-primary" type="button" onclick={() => (showAddform = true)}
				>Add New Slideshow</button
			>
		</div>
	{/if}
</div>
