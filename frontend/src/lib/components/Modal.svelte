<script lang="ts">
	import { slide } from 'svelte/transition';
	import { tick, type Snippet } from 'svelte';

	interface IProps {
		children: Snippet;
		closedBy?: 'any' | 'closerequest' | 'none';
		title: Snippet;
		footer?: Snippet;
	}
	let { children, title, closedBy = 'any', footer = undefined }: IProps = $props();
	let dialog: HTMLDialogElement;
	let isopen: boolean = $state(false);
	export function open() {
		if (dialog) dialog.showModal();
		tick().then((_) => (isopen = true));
	}
	export function close() {
		if (dialog) {
			dialog.close();
		}
	}
</script>

<dialog bind:this={dialog} closedby={closedBy}>
	{#if isopen}
		<form class="modal-content" transition:slide>
			<div class="modal-header">
				<h1 class="modal-title fs-5">
					{@render title()}
				</h1>
				<button class="btn-close" aria-label="Close" onclick={() => dialog.close()}></button>
			</div>
			<div class="modal-body mb-2">
				{@render children()}
			</div>
			{#if footer}
				<div class="modal-footer justify-content-between">
					{@render footer()}
				</div>
			{/if}
		</form>
	{/if}
</dialog>

<style>
	dialog {
		/*width: 80%;*/
		border-radius: 6px;
		padding: 0.5rem;
		--mo-modal-header-border-color: var(--mo-primary);
		--mo-modal-header-border-width: 1px;
		--mo-heading-color: var(--mo-primary);
		--mo-modal-header-padding: 0.25rem;
		--mo-modal-padding: 0.25rem;
	}

	/* Styles for the backdrop */
	dialog::backdrop {
		background-color: rgba(0, 0, 100, 0.7);
		backdrop-filter: blur(3px);
	}
</style>
