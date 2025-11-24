<script lang="ts">
	import { clickOutside } from '$lib/click-outside';
	import type { Snippet } from 'svelte';

	interface IProps {
		text: string;
		children: Snippet;
	}
	let { text, children }: IProps = $props();
	let menu: HTMLDivElement;
	let show = $state(false);
	function toggleShow() {
		show = !show;
	}
</script>

<li class="nav-item dropdown" use:clickOutside={() => (show = false)}>
	<button
		class="nav-link dropdown-toggle"
		type="button"
		data-bs-toggle="dropdown"
		onclick={toggleShow}
		aria-expanded="false"
	>
		{text}
	</button>
	<div class="dropdown-menu" bind:this={menu} style="display: {show ? 'block' : 'none'};">
		{@render children()}
	</div>
</li>
