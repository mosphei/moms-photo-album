<script lang="ts">
	import { derived, type Writable } from 'svelte/store';
	import type { IUpload } from './upload-file';

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
		'mb-3': true,
		'alert-secondary': $status == 'waiting',
		'alert-primary': $status == 'uploading',
		'alert-success': $status == 'complete',
		'alert-danger': $status == 'error'
	}}
>
	<strong>
		{fileEntry.filename}
		{$status}:
		{$result?.statusCode}
		{$result?.statusText}
	</strong>
	<div>
		{$result?.detail}
	</div>

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
