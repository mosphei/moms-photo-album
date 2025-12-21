<script lang="ts">
	import { derived, type Writable } from 'svelte/store';
	import type { IUpload } from './upload-file';
	import { type Photo, photoPath } from '$lib/models/photo';

	export interface IFileInfo {
		filename: string;
		file: File;
		uploadStatus: Writable<IUpload>;
	}
	interface IProps {
		fileEntry: IFileInfo;
	}
	let { fileEntry }: IProps = $props();
	let status = derived(fileEntry.uploadStatus, (US) => US.status);
	let percent = derived(fileEntry.uploadStatus, (US) => US.percentComplete);
	let result = derived(fileEntry.uploadStatus, (US) => US.result);
</script>

<div
	class={{
		alert: true,
		'me-3': true,
		'alert-secondary': $status == 'waiting',
		'alert-primary': $status == 'uploading',
		'alert-success': $status == 'complete',
		'alert-danger': $status == 'error'
	}}
>
	<strong>
		{fileEntry.filename}
	</strong>
	{#if $result?.statusCode == 200 && $result?.detail}
		{@const photo = JSON.parse($result.detail) as Photo}
		<img src={photoPath('t', photo)} alt={fileEntry.filename} />
		<div>{photo.date_taken}</div>
		<div>{photo.size}</div>
		<div>{photo.description}</div>
	{:else}
		<div>{$status}: {$result?.detail}</div>
	{/if}
	<div
		class="progress"
		role="progressbar"
		aria-label="{fileEntry.filename} {$status}"
		aria-valuenow={$percent}
		aria-valuemin="0"
		aria-valuemax="100"
	>
		<div class="progress-bar bg-{$percent < 100 ? '' : 'success'}" style="width: {$percent}%">
			{$percent}%
		</div>
	</div>
</div>

<style>
	.alert {
		width: 16rem;
	}
</style>
