<script lang="ts">
	import type { Snippet } from 'svelte';

	interface IProps {
		text: string;
		children: Snippet;
	}
	let { text, children }: IProps = $props();
	let menu: HTMLUListElement;
	let show = $state(false);
	function toggleShow() {
		show = !show;
		if (show) {
			menu.focus();
		}
	}

	function handleFocusOut(event: FocusEvent & { currentTarget: EventTarget & HTMLLIElement }) {
		event.preventDefault();
		setTimeout(() => {
			show = false;
		}, 300);
	}
</script>

<li class="nav-item dropdown" onfocusout={handleFocusOut}>
	<button
		class="nav-link dropdown-toggle"
		type="button"
		data-bs-toggle="dropdown"
		onclick={toggleShow}
		aria-expanded="false"
	>
		{text}
	</button>
	<ul class="dropdown-menu" bind:this={menu} style="display: {show ? 'block' : 'none'};">
		{@render children()}
	</ul>
</li>
