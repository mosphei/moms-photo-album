<script lang="ts">
	import { derived, get, writable, type Readable, type Writable } from 'svelte/store';
	import {
		fakeUploadFileWithProgress,
		uploadFileWithProgress,
		type IUpload,
		type IUploadResult
	} from './upload-file';
	import UploadCard, { type IFileInfo } from './UploadCard.svelte';

	const MAX = 2;

	let fileList: IFileInfo[] = $state([]);
	function onSelectFiles() {
		input.click();
	}
	let input: HTMLInputElement;
	let busy = $state(false);

	function handleOnChange(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		const files = input.files;
		if (files) {
			busy = true;
			fileList = [];
			const trackers: Writable<IUpload>[] = [];
			for (let i = 0; i < files.length; i++) {
				const file = files.item(i);
				if (file) {
					const fileEntry: IFileInfo = {
						filename: file.name,
						file: file,
						uploadStatus: writable({
							status: 'waiting',
							percentComplete: 0
						})
					};
					fileList = [...fileList, fileEntry];
					trackers.push(fileEntry.uploadStatus);

					if (i < MAX) {
						startUpload(fileEntry);
					}
				}
			}
			const alltrackers = derived(trackers, (ALL) => ALL);
			alltrackers.subscribe((ALL) => {
				console.log('alltrackers emitted');
				const uploading = ALL.filter((t) => t.status == 'uploading');
				if (uploading.length < MAX) {
					// start another
					const waiter = fileList.find((f) => get(f.uploadStatus).status === 'waiting');
					if (waiter) {
						startUpload(waiter);
					}
				}
				if (uploading.length === 0) {
					busy = false;
				}
			});
		}
	}
	function startUpload(fileEntry: IFileInfo) {
		fileEntry.uploadStatus.set({
			status: 'uploading',
			percentComplete: 0
		});
		uploadFileWithProgress('/api/images/upload/', fileEntry.file, (percentComplete) => {
			//console.log(`${fileEntry.filename}=${percentComplete}`);
			fileEntry.uploadStatus.set({
				status: 'uploading',
				percentComplete
			});
		})
			.then((result) => {
				fileEntry.uploadStatus.set({
					status: 'complete',
					percentComplete: 100,
					result: result
				});
			})
			.catch((err) => {
				fileEntry.uploadStatus.set({
					status: 'error',
					percentComplete: 0,
					result: err
				});
			});
	}
</script>

<h1>Upload</h1>
<p>Select one or more image files</p>
{#each fileList as f}
	<UploadCard fileEntry={f} />
{/each}
<button onclick={onSelectFiles} class="btn btn-primary" disabled={busy}>Upload</button>
<input
	type="file"
	bind:this={input}
	accept="image/*"
	multiple
	style="display:none"
	onchange={handleOnChange}
/>
