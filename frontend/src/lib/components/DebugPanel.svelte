<script lang="ts">
	import { dev } from '$app/environment';
	import type { Snippet } from 'svelte';

	interface IProps {
		value: any;
		children?: Snippet;
	}
	let { value, children }: IProps = $props();
</script>

{#if dev}
	<pre>{JSON.stringify(value, undefined, 2)}</pre>
	<div>
		{@render children?.()}
	</div>
{/if}
