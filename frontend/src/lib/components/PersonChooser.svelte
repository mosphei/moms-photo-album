<script lang="ts">
	import { createPopperActions } from 'svelte-popperjs';
	import type { PaginatedResults } from '$lib/models/paginated-results';
	import type { Person } from '$lib/models/person';
	import { fetchApi } from '$lib/stores/common-store';
	import DebugPanel from './DebugPanel.svelte';
	import { slide } from 'svelte/transition';

	interface IProps {
		onselect: (p: Person) => void;
	}
	let { onselect }: IProps = $props();
	const [popperRef, popperContent] = createPopperActions();
	let personText = $state('');
	let personSearchResult: Person[] = $state([]);
	let searchTimer: any;
	function handlePeopleSearch(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		const q = event.currentTarget.value;
		if (searchTimer) {
			clearTimeout(searchTimer);
		}
		searchTimer = setTimeout(async () => {
			if (q.length > 2) {
				const params = new URLSearchParams({ q, limit: '10' });
				const response = await fetchApi('/api/people/?' + params.toString());
				console.log('search resp', response);
				if (response) {
					const result: PaginatedResults<Person> = JSON.parse(response);
					personSearchResult = result.items;
				}
			} else {
				personSearchResult = [];
			}
		}, 300);
	}
	function clearSearch() {
		personText = '';
		personSearchResult = [];
		selectedIndex = -1;
	}
	function handleOnselect(p: Person): any {
		clearSearch();
		onselect(p);
	}

	let selectedIndex = $state(-1);
	let inputElement: HTMLInputElement | undefined = undefined;
	let menuElement: HTMLDivElement | undefined = $state();
	let buttonElements: HTMLButtonElement[] = $state([]);
	function handleKeyDown(event: KeyboardEvent & { currentTarget: EventTarget }) {
		// console.log(event.key);
		if (event.key === 'Escape') {
			event.preventDefault();
			clearSearch();
		}
		if (event.key === 'ArrowDown') {
			event.preventDefault();
			if (event.currentTarget == inputElement) {
				selectedIndex = 0;
			} else {
				selectedIndex = selectedIndex + 1;
				if (selectedIndex >= personSearchResult.length) {
					selectedIndex = 0;
				}
			}
		}
		if (event.key === 'ArrowUp') {
			event.preventDefault();
			if (event.currentTarget == inputElement) {
				selectedIndex = -1;
			} else {
				selectedIndex = selectedIndex - 1;
				if (selectedIndex < 0) {
					inputElement?.focus();
				}
			}
		}
	}
	$effect(() => {
		if (selectedIndex >= buttonElements.length) {
			selectedIndex = 0;
		}
		if (buttonElements[selectedIndex]) {
			buttonElements[selectedIndex].focus();
		}
	});
</script>

<div class="input-group">
	<input
		bind:this={inputElement}
		bind:value={personText}
		class="form-control"
		placeholder="Enter Name"
		name="person"
		style="width: 10rem;"
		oninput={handlePeopleSearch}
		onkeydown={handleKeyDown}
	/>
	<button class="btn btn-outline-secondary" aria-label="clear" type="button" onclick={clearSearch}>
		clear
	</button>
</div>
{#if personSearchResult.length}
	<div
		class="list-group"
		bind:this={menuElement}
		use:popperContent
		onkeydown={handleKeyDown}
		role="menu"
		tabindex="-1"
		transition:slide
	>
		{#each personSearchResult as p, i}
			<button
				bind:this={buttonElements[i]}
				class="list-group-item"
				type="button"
				onclick={() => handleOnselect(p)}
			>
				{p.name}
			</button>
		{/each}
	</div>
{/if}

<DebugPanel value={{ selectedIndex, personSearchResult }} />
