<script lang="ts">
	import PageTitle from '$lib/components/PageTitle.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import type { PaginatedResults } from '$lib/models/paginated-results';
	import { PaginatedStore } from '$lib/models/paginated-store';
	import type { Photo } from '$lib/models/photo';
	import { fetchApi } from '$lib/stores/common-store';
	import { dateTimeReviver } from '$lib/utils';
	import { onMount, tick } from 'svelte';
	import { get, writable } from 'svelte/store';

	const missingStore = new PaginatedStore<Photo>(async (page: number, numPerPage: number) => {
		const offset = (page - 1) * numPerPage;
		const urlParams = new URLSearchParams({
			offset: `${offset}`,
			limit: `${numPerPage}`
		});
		const url = '/api/admin/missing?' + urlParams.toString();
		const response = await fetchApi(url, {
			headers: { accept: 'application/json' }
		});
		console.log(url, response);
		const result: PaginatedResults<Photo> = JSON.parse(response || '[]', dateTimeReviver);
		return result;
	});
	const { currentPage, numPerPage, totalCount, currentItems, lastPage } = missingStore;
	let page = $state($currentPage);
	$effect(() => {
		console.log('new page', page);
		missingStore.setCurrentPage(page);
	});
	let busy = $state(false);
	/*
	const items = writable([] as Photo[]);
	const currentPage = writable(1);
	const numPerPage = writable(20);
	let total_count = $state(0);
	let last: number | undefined = $state();
	let searchTimerId: any = 0;
	function getMissingItems(page: number, pageSize: number) {
		if (searchTimerId) {
			clearTimeout(searchTimerId);
		}
		searchTimerId = setTimeout(async () => {
			busy = true;
			const offset = (page - 1) * pageSize;
			const urlParams = new URLSearchParams({
				offset: `${offset}`,
				limit: `${pageSize}`
			});
			const url = '/api/admin/missing?' + urlParams.toString();
			const response = await fetchApi(url, {
				headers: { accept: 'application/json' }
			});
			console.log(url, response);
			const result: PaginatedResults<Photo> = JSON.parse(response || '[]', dateTimeReviver);
			items.set(result.items);
			if (result.total_count) {
				total_count = result.total_count;
				last = Math.ceil(total_count / pageSize);
			}
			busy = false;
		}, 300);
	}
	currentPage.subscribe((pp) => {
		items.set([]);
		tick().then(() => getMissingItems(pp, $numPerPage));
	});
	numPerPage.subscribe((PS) => {
		// calculate new current page
		const currentFirstItem = ($currentPage - 1) * $numPerPage + 1;
		const newPage = Math.floor(currentFirstItem / $numPerPage) + 1;
		items.set([]);
		currentPage.set(newPage);
	});
    */
	onMount(() => {
		missingStore.refresh();
	});
</script>

<PageTitle title="Admin - Missing Photos">Missing Photos</PageTitle>

<div>
	{($currentPage - 1) * $numPerPage + 1}
	to {($currentPage - 1) * $numPerPage + $numPerPage}
	of {$totalCount}
</div>
{#if busy}
	<div class="alert alert-info">
		<div
			class="progress"
			role="progressbar"
			aria-label="Default striped example"
			aria-valuenow="10"
			aria-valuemin="0"
			aria-valuemax="100"
		>
			<div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 75%"></div>
		</div>
	</div>
{/if}
{#each $currentItems as item}
	<div class="card mb-2">
		<div class="card-body">
			<h5 class="card-title">
				{item.filename}
			</h5>
			<div>{item.content_type}</div>
			<p>
				{item.description}
			</p>
			{#if item.people?.length}
				{item.people.join(', ')}
			{/if}
		</div>
	</div>
{/each}
<div style="height:2.5rem">&nbsp;</div>
<div style="position:fixed;bottom:0">
	<Pagination bind:page width={7} last={$lastPage} />
</div>
