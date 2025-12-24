<script lang="ts">
	let { children } = $props();
</script>

<div class="modal-body mb-2">
	{@render children()}
</div>
