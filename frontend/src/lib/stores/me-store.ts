import { createFetcher, createStore } from './common-store';
import type { User } from '$lib/models/user';

const meFetcher = createFetcher<User>('/api/users/me', undefined, (response) => {
	const result: User = JSON.parse(response);
	return result;
});

export const me = createStore<User | undefined>(undefined, 'me', meFetcher);
// fire at least once
setTimeout(me.refresh, 300);
