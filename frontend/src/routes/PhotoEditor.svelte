<script lang="ts">
	import { errorAlert, progressAlert } from '$lib/alerts';
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import type { PaginatedResults } from '$lib/models/paginated-results';
	import type { Person } from '$lib/models/person';
	import { photoPath, type Photo } from '$lib/models/photo';
	import { fetchApi } from '$lib/stores/common-store';
	import { savePhoto } from '$lib/stores/photo-store';
	import { SvelteToast } from '@zerodevx/svelte-toast';
	import { onMount } from 'svelte';

	interface IProps {
		photos: Photo[];
		onsave?: () => void;
		oncancel?: () => void;
	}
	let { photos, onsave, oncancel }: IProps = $props();

	function handleCancel(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		searchText = '';
		fieldsToUpdate = [];
		if (oncancel) oncancel();
	}
	let busy = $state(false);

	async function applyAndSave(photo: Photo, changes: Partial<Photo>) {
		const msg = progressAlert(`saving ${photo.filename}`, { target: 'savetoast' });
		try {
			if ('date_taken' in changes) {
				// apply the original hh:mm:ss so they sort correctly later
				changes.date_taken?.setHours(photo.date_taken.getHours());
				changes.date_taken?.setMinutes(photo.date_taken.getMinutes());
				changes.date_taken?.setSeconds(photo.date_taken.getSeconds());
			}
			await savePhoto(photo.id, changes);
		} catch (err) {
			errorAlert(`unable to save ${photo.filename}`, err, 15000, { target: 'savetoast' });
			throw err;
		} finally {
			msg.dismiss();
		}
	}
	function save(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		const updates: Partial<Photo> = {};
		fieldsToUpdate.forEach((f) => {
			switch (f) {
				case 'date_taken':
					updates[f] = new Date(date_taken + 'T00:00:00');
					break;
				case 'description':
					updates[f] = description;
					break;
				case 'people':
					updates[f] = people;
			}
		});
		Promise.all(photos.map((photo) => applyAndSave(photo, updates)))
			.then(() => {
				searchText = '';
				fieldsToUpdate = [];
				if (onsave) onsave();
			})
			.catch((err) => {
				console.log('err', err);
				busy = false;
			});
	}

	// get initial values
	let originalValues: any = $state({});
	function dedupeAndJoin(values: string[]): string {
		return Array.from(
			new Set(
				values.map((v) => {
					if (!v) {
						return 'empty';
					}
					if (v.length > 10) {
						return `${v.substring(0, 7)}...`;
					}
					return v;
				})
			)
		).join(',');
	}
	$effect(() => {
		// parse original values
		originalValues = {
			date_taken: dedupeAndJoin(
				photos.map((p) => (p.date_taken ? p.date_taken.toLocaleDateString() : ''))
			),
			description: dedupeAndJoin(photos.map((p) => p.description || '')),
			people: dedupeAndJoin(photos.flatMap((p) => p.people).map((p) => p.name))
		};
	});
	let fieldsToUpdate: string[] = $state([]);
	let date_taken = $state('');
	let description = $state('');
	let rotate = $state(0);

	let people: Person[] = $state([]);
	let personInput: HTMLInputElement;
	let searchText = $state('');
	let searchResult: Person[] = $state([]);
	let searchTimer: any;
	async function handlePeopleSearch(
		event: Event & { currentTarget: EventTarget & HTMLInputElement }
	) {
		if (searchTimer) {
			clearTimeout(searchTimer);
		}
		const q = event.currentTarget.value;
		if (q) {
			const params = new URLSearchParams({ q, limit: '10' });
			const response = await fetchApi('/api/people/?' + params.toString());
			console.log('search resp', response);
			if (response) {
				const result: PaginatedResults<Person> = JSON.parse(response);
				searchResult = result.items;
			}
		}
	}

	function addPerson(p: Person): any {
		const idx = people.findIndex((x) => x.id === p.id);
		if (idx < 0) {
			people = [...people, p];
			searchResult = [];
			searchText = '';
			personInput.focus();
		}
	}

	function removePerson(person: Person): any {
		people = [...people.filter((p) => p.id != person.id)];
	}

	async function createPerson(name: string) {
		try {
			const response = await fetchApi('/api/people/new', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name })
			});
			if (response) {
				const result: Person = JSON.parse(response);
				addPerson(result);
			}
		} catch (err) {
			errorAlert('unable to create person ' + name, err, 15000, { target: 'savetoast' });
		}
	}
	onMount(() => {
		console.log('PhotoEditor.svelte');
	});
</script>

<div class="d-flex flex-wrap mb-2" style="width: 100%;--rotation:{rotate}deg;">
	{#each photos as photo}
		<div style="margin:4px; width: 200px; height:200px">
			<img
				src={photoPath('t', photo)}
				alt={photo.filename}
				style="object-fit: contain;width:100%;height:100%;transform:rotate(var(--rotation,0));transform-origin:center center"
			/>
		</div>
	{/each}
</div>

<div class="mb-3">
	<p>Unchecked attributes will not be changed on the target photos.</p>
	<div class="mb-2">
		<label for="date">Date</label>
		<div class="input-group">
			<div class="input-group-text">
				<input
					type="checkbox"
					value="date_taken"
					bind:group={fieldsToUpdate}
					class="form-check-input"
				/>
			</div>
			<input
				type={fieldsToUpdate.includes('date_taken') ? 'date' : 'text'}
				class="form-control"
				bind:value={date_taken}
				placeholder={originalValues.date_taken}
				name="date"
				id="date"
				disabled={!fieldsToUpdate.includes('date_taken')}
			/>
		</div>
	</div>
	<div class="mb-2">
		<!-- description -->
		<label for="description">Description</label>
		<div class="input-group">
			<div class="input-group-text">
				<input
					type="checkbox"
					value="description"
					bind:group={fieldsToUpdate}
					class="form-check-input"
				/>
			</div>
			<input
				type="text"
				class="form-control"
				bind:value={description}
				name="description"
				id="description"
				placeholder={originalValues.description}
				disabled={!fieldsToUpdate.includes('description')}
			/>
		</div>
	</div>
	<div class="mb-2">
		<!-- people chooser-->
		<label for="people">People</label>
		<div class={{ ppl: true, enabled: fieldsToUpdate.includes('people') }}>
			<div style="padding: .375rem .75rem;">
				<input
					type="checkbox"
					value="people"
					bind:group={fieldsToUpdate}
					class="form-check-input"
				/>
			</div>
			{#if fieldsToUpdate.includes('people')}
				{#each people as p}
					<div class="chip">
						{p.name}
						<button class="" onclick={() => removePerson(p)} aria-label="remove" type="button">
							{#if fieldsToUpdate.includes('people')}
								<span class="bi bi-trash"></span>
							{/if}
						</button>
					</div>
				{/each}
				<div style="width: 20rem;">
					<input
						type="text"
						class="form-control"
						name="description"
						id="description"
						disabled={!fieldsToUpdate.includes('people')}
						oninput={handlePeopleSearch}
						bind:this={personInput}
						placeholder={fieldsToUpdate.includes('people') ? 'name search' : originalValues.people}
						bind:value={searchText}
						autocomplete="off"
					/>
					{#if searchText.length}
						<ul class="dropdown-menu show">
							{#each searchResult as p}
								<li>
									<button class="dropdown-item" type="button" onclick={() => addPerson(p)}>
										{p.name}
									</button>
								</li>
							{/each}
							<li>
								<button
									class="dropdown-item"
									type="button"
									onclick={() => createPerson(searchText)}
								>
									New Person '{searchText}'
								</button>
							</li>
						</ul>
					{/if}
				</div>
			{:else}
				<div style="width: 20rem;">
					<input class="form-control" type="text" disabled placeholder={originalValues.people} />
				</div>
			{/if}
		</div>
	</div>
	<div class="mb-2">
		<label for="date">Rotate</label>
		<div class="input-group">
			<div class="input-group-text">
				<input
					type="checkbox"
					value="rotate"
					bind:group={fieldsToUpdate}
					class="form-check-input"
				/>
			</div>
			<select
				name="rotate"
				id="rotate"
				class="form-select"
				bind:value={rotate}
				disabled={!fieldsToUpdate.includes('rotate')}
			>
				<option value={0}>Rotate:</option>
				<option value={270}>left</option>
				<option value={90}>right</option>
				<option value={180}>180</option>
			</select>
		</div>
	</div>
</div>
<div class="d-flex justify-content-between">
	<button class="btn btn-primary" onclick={save} disabled={busy || !fieldsToUpdate.length}
		>Save</button
	>
	<button class="btn btn-secondary" type="button" onclick={handleCancel}>Cancel</button>
</div>
<SvelteToast target="savetoast" />
<DebugPanel value={{ originalValues }} />

<style>
	.ppl {
		border: solid 1px;
		border-color: var(--mo-border-color, gray);
		border-radius: var(--mo-border-radius, 4px);
		display: flex;
		flex-wrap: wrap;
		align-items: center;
	}
	.chip {
		margin: 0.25rem;
		padding: 0.25rem;
		background-color: var(--mo-secondary-bg-subtle);
	}
	.chip:hover {
		background-color: var(--mo-secondary-bg);
	}
	.chip button {
		border: none;
		background: transparent;
	}
</style>
