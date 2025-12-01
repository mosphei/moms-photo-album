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
	<li class={{ 'page-item': true, disabled: page <= 1 }}>
		<button onclick={() => (page = 1)} class="page-link" disabled={page <= 1}>First</button>
	</li>
	<li class={{ 'page-item': true, disabled: page <= 1 }}>
		<button onclick={() => (page = page - 1)} class="page-link" disabled={page <= 1}
			>Previous</button
		>
	</li>
	{#each pages as p}
		{@const active = p == page}
		<li class={{ active, 'page-item': true, disabled: active }}>
			<button class="page-link" onclick={() => (page = p)} disabled={active}>{p}</button>
		</li>
	{/each}
	<li class={{ 'page-item': true, disabled: last && page >= last }}>
		<button
			class="page-link"
			onclick={() => (page = page + 1)}
			disabled={last ? page >= last : false}>Next</button
		>
	</li>
	{#if last}
		<li class={{ 'page-item': true, disabled: page >= last }}>
			<button class="page-link" onclick={() => (page = last)} disabled={page >= last}>Last</button>
		</li>
	{/if}
</ul>
