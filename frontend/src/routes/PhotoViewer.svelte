<script lang="ts">
	import { photoPath, type Photo } from '$lib/models/photo';
	import { IMAGESIZES, type SizeEnum } from '$lib/models/settings';

	interface iProps {
		size?: SizeEnum;
		photo: Photo;
	}
	let { size = undefined, photo }: iProps = $props();
	const imgSize = size ? size : 'm';
	let [width, height] = IMAGESIZES[imgSize];
</script>

<div style="width: {width}px;height:{height}px">
	<img
		src={photoPath('m', photo)}
		alt={photo.filename}
		style="object-fit:
 contain;object-position:center;width:100%;height:100%"
	/>
</div>
