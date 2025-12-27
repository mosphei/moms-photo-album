<script lang="ts">
	import { onMount, type Snippet } from 'svelte';

	interface IProps {
		onclose?: () => void;
		children: Snippet;
		dialog?: HTMLDialogElement;
	}
	let { onclose, children, dialog = $bindable() }: IProps = $props();

	//let dialog: HTMLDialogElement | undefined = $state();

	function handleClose(event: Event & { currentTarget: EventTarget & HTMLDialogElement }) {
		event.preventDefault();
		onclose?.();
		history.back();
	}

	onMount(() => {
		dialog?.showModal();
	});
</script>

<dialog bind:this={dialog} closedby="any" onclose={handleClose}>
	{@render children()}
</dialog>

<style>
	dialog {
		/*width: 80%;*/
		background: var(--background, #fff);
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
