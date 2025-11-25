<script lang="ts">
	import Progress from '$lib/components/Progress.svelte';
	import { get, writable, type Writable } from 'svelte/store';

	interface IFileInfo {
		filename: string;
		percentComplete: Writable<number>;
	}
	function uploadFileWithProgress(url: string, file: File, progressCallback: (e: number) => void) {
		return new Promise((resolve, reject) => {
			let percent = 0;
			const millseconds = Math.ceil(Math.random() * 300);
			let timerid = setInterval(() => {
				percent += 1;
				progressCallback(percent);
				if (percent >= 100) {
					clearInterval(timerid);
					resolve(true);
				}
			}, millseconds);
		});
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

					uploadFileWithProgress('/api/images/upload', file, (p) => {
						fileEntry.percentComplete.set(p);
						console.log(`p=${p}`);
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
<button onclick={onSelectFiles}>Upload</button>
<input
	type="file"
	bind:this={input}
	accept="image/*"
	multiple
	style="display:none"
	onchange={handleOnChange}
/>
