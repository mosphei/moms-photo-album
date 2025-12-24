<script lang="ts">
	import PageTitle from '$lib/components/PageTitle.svelte';
	import type { PageProps } from '../$types';

	let { data }: PageProps = $props();
	$inspect(data);
</script>

<PageTitle title={data.id}>
	<h1>Slideshow</h1>
</PageTitle>
