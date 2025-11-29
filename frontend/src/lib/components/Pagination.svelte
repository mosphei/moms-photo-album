<script lang="ts">
	import { rangeAroundCenter } from '$lib/utils';

	interface IProps {
		page: number;
		last?: number;
		width?: number; // number of pages to show
	}
	let { page = $bindable(), last = undefined, width = 3 }: IProps = $props();
	let pages = $state([page]);
	$effect(() => {
		const max = last ? last : page + 1;
		pages = rangeAroundCenter(page, width, max);
	});
</script>

<ul class="pagination">
	<li class="page-item">
		<button onclick={() => (page = 1)} class="page-link" disabled={page <= 1}>First</button>
	</li>
	<li class="page-item">
		<button onclick={() => (page = page - 1)} class="page-link" disabled={page <= 1}
			>Previous</button
		>
	</li>
	{#each pages as p}
		{@const active = p == page}
		<li class={{ active, 'page-item': true }}>
			<button class="page-link" onclick={() => (page = p)} disabled={active}>{p}</button>
		</li>
	{/each}
	<li class="page-item">
		<button
			class="page-link"
			onclick={() => (page = page + 1)}
			disabled={last ? page >= last : false}>Next</button
		>
	</li>
	{#if last}
		<li class="page-item">
			<button class="page-link" onclick={() => (page = last)} disabled={page == last}>Last</button>
		</li>
	{/if}
</ul>
