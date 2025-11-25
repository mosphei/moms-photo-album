<script lang="ts">
	import { type Readable } from 'svelte/store';
	interface IProps {
		label: string;
		percent: Readable<number>;
	}
	let { label, percent }: IProps = $props();
</script>

<div>{label}</div>
<div
	class="progress"
	role="progressbar"
	aria-label={label}
	aria-valuenow={$percent}
	aria-valuemin="0"
	aria-valuemax="100"
>
	<div class="progress-bar bg-{$percent < 100 ? '' : 'success'}" style="width: {$percent}%">
		{$percent}%
	</div>
</div>
