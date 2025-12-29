<script lang="ts">
	import { resolve } from '$app/paths';
	import { errorAlert, progressAlert } from '$lib/alerts';
	import PageTitle from '$lib/components/PageTitle.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import type { Slideshow } from '$lib/models/slideshow';
	import { saveSlideshow, slideshowStore } from '$lib/stores/slideshow-store';
	import { onMount } from 'svelte';
	import { slide } from 'svelte/transition';

	let { currentPage, lastPage, numPerPage, totalCount, currentItems } = slideshowStore;
	let page = $state($currentPage);
	$effect(() => {
		slideshowStore.setCurrentPage(page);
	});
	// other direction too
	currentPage.subscribe((pp) => {
		page = pp;
	});
	function handleLimitChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
		const x = parseInt(event.currentTarget.value);
		slideshowStore.setNumPerPage(x);
	}

	let showAddform = $state(false);
	async function handleAddNew(
		event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }
	) {
		event.preventDefault();
		const msg = progressAlert('adding new slideshow');
		try {
			const vals = new FormData(event.currentTarget);
			const title = vals.get('title') as string;
			if (title === '') {
				throw new Error('title is required');
			}
			saveSlideshow({
				id: 0,
				title: title,
				slides: []
			});
		} catch (error) {
			errorAlert('unable to ad slideshow ', error, 15000);
		} finally {
			msg.dismiss();
		}
	}

	onMount(async () => {
		try {
			await slideshowStore.refresh();
		} catch (error) {
			errorAlert('unable to get slideshows', error, 15000);
		}
	});
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
			{slideshow.slide_count}
			slide{slideshow.slide_count === 1 ? '' : 's'}
		</p>
	</div>
{/snippet}

<div class="list-group mb-3">
	{#if $totalCount !== undefined && $totalCount < 1}
		<div class="list-group-item">No items found.</div>
	{/if}
	{#each $currentItems as slideshow (slideshow.id)}
		<a
			class="list-group-item list-group-item-action"
			href={resolve('/slideshows/[slug]', { slug: slideshow.id.toString() })}
			title="edit"
		>
			{slideshow.title}
			<span class="badge text-bg-primary rounded-pill">
				{slideshow.slide_count}
			</span>
		</a>
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
		<button
			class="list-group-item list-group-item-action"
			type="button"
			onclick={() => (showAddform = true)}
		>
			Add New Slideshow
		</button>
	{/if}
</div>

<!-- footer -->
<div style="clear: both;position:sticky;bottom:4px" class="row g-3">
	<div class="col-auto">
		<Pagination last={$lastPage} bind:page />
	</div>
	<div class="col-auto">
		<div class="input-group">
			<span class="input-group-text"> Show </span>
			<select name="nmn" value={$numPerPage} onchange={handleLimitChange} class="form-select">
				{#each [10, 20, 50, 100] as val}
					<option>{val}</option>
				{/each}
			</select>
		</div>
	</div>
</div>
