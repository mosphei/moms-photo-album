<script lang="ts">
	import Progress from '$lib/components/Progress.svelte';
	import { get, writable, type Writable } from 'svelte/store';
	import { uploadFileWithProgress } from './upload-file';
	import { session } from '$lib/stores/session-store';

	interface IFileInfo {
		filename: string;
		percentComplete: Writable<number>;
	}
	let fileList: IFileInfo[] = $state([]);
	function onSelectFiles() {
		input.click();
	}
	let input: HTMLInputElement;

	function handleOnChange(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		const files = input.files;
		if (files) {
			for (let i = 0; i < files.length; i++) {
				const file = files.item(i);
				if (file) {
					const fileEntry: IFileInfo = {
						filename: file.name,
						percentComplete: writable(0)
					};
					const headers = {
						Authorization: `Bearer ${get(session.token)?.access_token}`
					};
					uploadFileWithProgress(
						'/api/images/upload/',
						file,
						(p) => {
							console.log(`p=${p}`);
							fileEntry.percentComplete.set(p);
						},
						headers
					).catch((err) => {
						alert(`Unable to send file: ${err}`);
					});
					fileList = [...fileList.filter((fentry) => get(fentry.percentComplete) < 100), fileEntry];
				}
			}
		}
	}
</script>

<h1>Upload</h1>
<p>Select one or more image files</p>
{#each fileList as f}
	<div class="mb-2">
		<Progress label={f.filename} percent={f.percentComplete} />
	</div>
{/each}
<button onclick={onSelectFiles} class="btn btn-primary">Upload</button>
<input
	type="file"
	bind:this={input}
	accept="image/*"
	multiple
	style="display:none"
	onchange={handleOnChange}
/>
