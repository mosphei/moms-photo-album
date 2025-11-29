import { browser } from '$app/environment';
import { get, type Readable, writable } from 'svelte/store';
import { session, type TokenResponse } from './session-store';
import { deepMerge } from '$lib/utils';

export async function fetchApi(url: string, opts = {}) {
	if (browser) {
		const token = get(session.token);
		const fetchOpts = deepMerge({
			method: 'GET',
			headers: {
				Authorization: token ? `${token.token_type} ${token.access_token}` : 'undefined'
			}
		}, opts);
		console.log('fetchOpts', fetchOpts);
		const response = await fetch(url, fetchOpts);
		if (!response.ok) {
			if (response.status === 401) {
				session.clearToken();
			}
			const result = await response.text();
			console.log('Error getting data: ', result, response);
			throw result;
		}
		const txt = await response.text();
		return txt;
	}
	//return 'undefined';
}

export function createFetcher<T>(
	url: string,
	opts: any,
	callback: (response: string) => T
): () => Promise<T | undefined> {
	return async () => {
		const txt = await fetchApi(url, opts);
		if (txt) {
			const x = callback(txt);
			return x;
		}
	};
}

export function createStore<T>(
	intitalValue: T,
	localStorageKey: string,
	fetcher: () => Promise<T | undefined>
): Readable<T> & { refresh: () => Promise<boolean> } {
	const { subscribe, update } = writable<T>(intitalValue);
	let fetchDebounceId: any = 0;
	let block = false;
	return {
		subscribe,
		refresh: () => {
			return new Promise((resolve, reject) => {
				const updaterFunc = () => {
					if (block) {
						if (fetchDebounceId) {
							clearTimeout(fetchDebounceId);
						}
						fetchDebounceId = setTimeout(updaterFunc, 300);
						return;
					}
					block = true;
					fetcher()
						.then((newval) => {
							if (newval) {
								update(() => newval);
							}
						})
						.catch((err) => reject(err))
						.finally(() => (block = false));
				};
				if (fetchDebounceId) {
					clearTimeout(fetchDebounceId);
				}
				fetchDebounceId = setTimeout(updaterFunc, 300);
				// even if timeout is cleared, resolves on next update
				subscribe(() => resolve(true));
			});
		}
	};
}
