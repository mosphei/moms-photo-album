<script lang="ts">
	import { beforeNavigate } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { clickOutside } from '$lib/click-outside';
	import { me } from '$lib/stores/me-store';
	import { session } from '$lib/stores/session-store';
	import NavDropdown from './NavDropdown.svelte';

	function handleLogout(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
		session.clearToken();
	}

	let show = $state(false);

	function handleOutsideClick() {
		show = false;
	}
	beforeNavigate((navigation) => {
		show = false;
	});
</script>

<nav class="navbar navbar-expand-lg bg-body-tertiary" use:clickOutside={handleOutsideClick}>
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
			onclick={() => (show = !show)}
		>
			{show}
			<span class="navbar-toggler-icon"></span>
		</button>
		<div class="collapse navbar-collapse" class:show id="navbarSupportedContent">
			<ul class="navbar-nav me-auto mb-2 mb-lg-0">
				<li class="nav-item">
					<a class="nav-link" aria-current="page" href="/">Home</a>
				</li>
				<li class="nav-item">
					<a href={resolve('/upload')} class="nav-link">Upload</a>
				</li>
				<!--
				<NavDropdown text="Dropdown">
					<a class="dropdown-item" href="/xxx">X</a>
					<a class="dropdown-item" href="/xxx">X</a>
					<a class="dropdown-item" href="/xxx">X</a>
					<hr class="dropdown-divider" />
					<a class="dropdown-item" href="/xxx">X</a>
				</NavDropdown>
				<li class="nav-item">
					<a class="nav-link disabled" aria-disabled="true">Disabled</a>
				</li> 
				-->
			</ul>
			<form class="d-flex me-2" role="search">
				<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" />
				<button class="btn btn-outline-success" type="submit">Search</button>
			</form>
			{#if $me}
				<ul class="navbar-nav mb-2 mb-lg-0">
					<NavDropdown text={$me.username}>
						<button class="dropdown-item" onclick={handleLogout}> Log Out </button>
					</NavDropdown>
				</ul>
			{/if}
		</div>
	</div>
</nav>
