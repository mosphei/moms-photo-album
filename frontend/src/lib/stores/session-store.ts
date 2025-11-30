import { browser } from '$app/environment';
import { derived, writable } from 'svelte/store';

export const session = writable(undefined as boolean | undefined);
