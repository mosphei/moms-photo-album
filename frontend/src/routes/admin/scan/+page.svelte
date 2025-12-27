<script lang="ts">
	import PageTitle from '$lib/components/PageTitle.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import type { PaginatedResults } from '$lib/models/paginated-results';
	import { PaginatedStore } from '$lib/models/paginated-store';
	import type { Photo } from '$lib/models/photo';
	import { fetchApi } from '$lib/stores/common-store';
	import { dateTimeReviver } from '$lib/utils';
	async function fetcher(page: number, numPerPage: number) {
		const offset = (page - 1) * numPerPage;
		const urlParams = new URLSearchParams({
			offset: `${offset}`,
			limit: `${numPerPage}`
		});
		const url = '/api/admin/scan?' + urlParams.toString();
		const response = await fetchApi(url, {
			headers: { accept: 'application/json' }
		});
		const result: PaginatedResults<Photo> = JSON.parse(response || '[]', dateTimeReviver);
		console.log(url, result);
		return result;
	}
	const scanStore = new PaginatedStore<Photo>(fetcher);
	const { currentPage, numPerPage, totalCount, currentItems, lastPage } = scanStore;
	let page = $state($currentPage);
	$effect(() => {
		console.log('new page', page);
		scanStore.setCurrentPage(page);
	});
</script>

<PageTitle title="Admin - Scan For New">Scan for New Photos</PageTitle>

<div>
	{($currentPage - 1) * $numPerPage + 1}
	to {($currentPage - 1) * $numPerPage + $numPerPage}
	of {$totalCount}
</div>
{#each $currentItems as item (item.id)}
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
