import { createFetcher, createStore } from './common-store';
import type { User } from '$lib/models/user';
import { session } from './session-store';
import { get } from 'svelte/store';

const meFetcher = createFetcher<User | undefined>('/api/users/me', undefined, (response) => {
	const user = JSON.parse(response);
	if (user && get(session) !== true) {
		session.set(true);
	}
	return user;
});

export const me = createStore<User | undefined>(undefined, 'me', meFetcher);
// fire at least once
setTimeout(me.refresh, 300);
