<script lang="ts">
	import { me } from '$lib/stores/me-store';
	import NavDropdown from './NavDropdown.svelte';
</script>

<nav class="navbar navbar-expand-lg bg-body-tertiary">
	<div class="container-fluid">
		<a class="navbar-brand" href="/">Photos</a>
		<button
			class="navbar-toggler"
			type="button"
			data-bs-toggle="collapse"
			data-bs-target="#navbarSupportedContent"
			aria-controls="navbarSupportedContent"
			aria-expanded="false"
			aria-label="Toggle navigation"
		>
			<span class="navbar-toggler-icon"></span>
		</button>
		<div class="collapse navbar-collapse" id="navbarSupportedContent">
			<ul class="navbar-nav me-auto mb-2 mb-lg-0">
				<li class="nav-item">
					<a class="nav-link" aria-current="page" href="/">Home</a>
				</li>
				<NavDropdown
					text="Dropdown"
					links={[
						{ href: '/xxx', text: 'X' },
						{ href: '/yyy', text: 'Y' },
						'divider',
						{ href: '/zzz', text: 'Z' }
					]}
				/>
				<li class="nav-item">
					<a class="nav-link disabled" aria-disabled="true">Disabled</a>
				</li>
			</ul>
			<form class="d-flex" role="search">
				<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" />
				<button class="btn btn-outline-success" type="submit">Search</button>
			</form>
			{#if $me}
				<NavDropdown text={$me.username} links={[]} />

			{/if}
		</div>
	</div>
</nav>
