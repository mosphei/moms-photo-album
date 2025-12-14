<script lang="ts">
	import { version } from '$app/environment';
	import { errorAlert, progressAlert } from '$lib/alerts';
	import DebugPanel from '$lib/components/DebugPanel.svelte';
	import gitversion from './gitversion.json' with { type: 'json' };

	const sleep = (t = Math.random() * 1000) => new Promise((resolve) => setTimeout(resolve, t));
	async function throwError() {
		const msg = progressAlert('testing errors and loading bars');
		try {
			await sleep(3000);
			throw new Error('Test of the error broadcasting network...');
		} catch (error) {
			console.log('error', error);
			const eMsg = errorAlert('error', error, 60000);
		} finally {
			msg.dismiss();
		}
	}

	async function throwAsync() {
		try {
			const response = await fetch('api/about', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify('about')
			});

			if (!response.ok) {
				const result = await response.text();
				throw Error('Post About: ' + result);
			}
		} catch (err) {
			const msg = errorAlert('test', err, 50000);
		}
	}
</script>

<h2>About</h2>
<p>Moms Photo Album</p>
<p>
	build: {version}
</p>
<!--
<DebugPanel value={{gitversion}} />
-->

<dl class="row">
	{#each Object.keys(gitversion) as key}
		<dt class="col-sm-3">{key}</dt>
		<dd class="col-sm-9">
			{gitversion[key]}
		</dd>
	{/each}
</dl>
<div id="actionbuttons">
	<span class="flex-grow-1"></span>
	<button class="btn btn-info border me-2" onclick={throwError}>Test Error</button>
	<button class="btn btn-info border me-2" onclick={throwAsync}>Async Error</button>
</div>
