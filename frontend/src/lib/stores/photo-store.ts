import type { PaginatedResults } from '$lib/models/paginated-results';
import type { Photo } from '$lib/models/photo';
import { MEDIAPATH, type SizeEnum } from '$lib/models/settings';
import { dateTimeReviver, loadFromLocalstorage, setLocalstorage } from '$lib/utils';
import { derived, writable, type Writable } from 'svelte/store';
import { createFetcher, createStore, fetchApi } from './common-store';
import { browser } from '$app/environment';

async function getPhotos(page: number, pagesize: number): Promise<PaginatedResults<Photo> | null> {
	if (page < 1) {
		return null;
	}
	const offset = (page - 1) * pagesize;
	const url = `/api/images/?offset=${offset}&limit=${pagesize}`;
	console.log(`url:${url}`);
	const response = await fetchApi(url, {
		headers: { accept: 'application/json' }
	});
	const result: PaginatedResults<Photo> = await JSON.parse(response || '[]', dateTimeReviver);
	console.log(`getPhotos`, result);
	return result;
}

const itemList = writable([] as Photo[]);
const initialNumPerPage = loadFromLocalstorage('numPerPage') || '10';
const numPerPage = writable(parseInt(initialNumPerPage));
numPerPage.subscribe((n) => setLocalstorage('numPerPage', n));
const currentPage = writable(0);
const totalItems = writable(null as null | number);
const changes = derived([currentPage, numPerPage], ([CurrentPage, NumPerPage]) => {
	getPhotos(CurrentPage, NumPerPage).then((result) => {
		if (result) {
			itemList.set(result.items);
			if (result.total_count) {
				totalItems.set(result.total_count);
			}
		}
	}); // catch?
});
changes.subscribe((x) => console.log('changed'));

export const photopages = {
	items: derived(itemList, (_) => _),
	numPerPage,
	currentPage,
	totalItems
};
// load the first page
currentPage.set(1);
