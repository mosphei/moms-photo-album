<script lang="ts">
	import type { Snippet } from 'svelte';

	interface IProps {
		children: Snippet;
		onCloseButton: () => void;
	}
	let { children, onCloseButton }: IProps = $props();
</script>

<div class="modal-header">
	<h1 class="modal-title fs-5">
		{@render children()}
	</h1>
	<button class="btn-close" aria-label="Close" onclick={onCloseButton}></button>
</div>
