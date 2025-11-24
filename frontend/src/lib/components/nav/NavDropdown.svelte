<script lang="ts">
	interface IProps {
		text: string;
		links: ({ text: string; href: string } | 'divider')[];
	}
	let { text, links }: IProps = $props();
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
		{#each links as link}
			<li>
				{#if link === 'divider'}
					<hr class="dropdown-divider" />
				{:else}
					<a class="dropdown-item" href={link.href}>{link.text}</a>
				{/if}
			</li>
		{/each}
	</ul>
</li>
