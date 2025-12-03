<script lang="ts">
	import { errorAlert, progressAlert } from '$lib/alerts';
	import { photoPath, type Photo } from '$lib/models/photo';
	import { savePhoto } from '$lib/stores/photo-store';
	import { SvelteToast } from '@zerodevx/svelte-toast';

	interface IProps {
		photos: Photo[];
		onsave?: () => void;
		oncancel?: () => void;
	}
	let { photos, onsave, oncancel }: IProps = $props();

	function handleCancel(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
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
			}
		});
		Promise.all(photos.map((photo) => applyAndSave(photo, updates)))
			.then(() => {
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
		console.log('parsing photos', photos);
		originalValues = {
			date_taken: dedupeAndJoin(
				photos.map((p) => (p.date_taken ? p.date_taken.toLocaleDateString() : ''))
			),
			description: dedupeAndJoin(photos.map((p) => p.description || '')),
			people: dedupeAndJoin(photos.flatMap((p) => p.people))
		};
	});
	let fieldsToUpdate: string[] = $state([]);
	let date_taken = $state('');
	let description = $state('');
	let rotate = $state(0);
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
		<label for="people">People</label>
		<div class="input-group">
			<div class="input-group-text">
				<input
					type="checkbox"
					value="people"
					bind:group={fieldsToUpdate}
					class="form-check-input"
				/>
			</div>
			<input
				type="text"
				class="form-control"
				name="description"
				id="description"
				disabled={!fieldsToUpdate.includes('people')}
			/>
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
