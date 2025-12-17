<script lang="ts">
	import { resolve } from '$app/paths';

	const sections: { href: string; title: string; blurb: string }[] = [
		{
			href: resolve('/admin/missing/'),
			title: 'Missing Photos',
			blurb: 'Remove photos that are in the database but not on the disk'
		},
		{
			title: 'Scan for new photos',
			href: resolve('/admin/scan/'),
			blurb: 'Find files on disk not in database'
		},
		{
			title: 'Users',
			href: resolve('/admin/users/'),
			blurb: 'Add users, set passwords, etc.'
		}
	];
</script>

<h1>Admin</h1>
{#each sections as section}
	<a class="card mb-3" href={section.href}>
		<div class="card-body">
			<h3 class="card-title">
				{section.title}
			</h3>
			<p>{section.blurb}</p>
		</div>
	</a>
{/each}

<style>
	a.card {
		text-decoration: none;
	}
	a.card:hover {
		border-color: var(--mo-primary);
	}
</style>
