<script lang="ts">
	let { children } = $props();
</script>

<div class="modal-footer justify-content-between">
	{@render children()}
</div>
