import { browser } from '$app/environment';
import { type Readable, writable } from 'svelte/store';

export async function fetchApi(url: string, opts = {}) {
	const fetchOpts = {
		...(opts || {}),
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		}
	};
	const response = await fetch(url, fetchOpts);
	if (!response.ok) {
		const result = await response.text();
		console.log('Error getting data: ', result);
		throw result;
	}
	const txt = await response.text();
	return txt;
}

export function createFetcher<T>(
	url: string,
	opts: any,
	callback: (response: string) => T
): () => Promise<T | undefined> {
	return async () => {
		if (browser) {
			const token: string = localStorage.access_token || '';
			const fetchOpts = {
				...(opts || {}),
				method: 'GET',
				headers: {
					Authorization: `Bearer ${token}`
				}
			};
			const response = await fetch(url, fetchOpts);
			if (!response.ok) {
				const result = await response.text();
				console.log('Error getting data: ', result);
				throw result;
			}
			const txt = await response.text();
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
