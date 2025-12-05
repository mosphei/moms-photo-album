import type { PaginatedResults } from '$lib/models/paginated-results';
import type { Photo } from '$lib/models/photo';
import { dateFormat, dateTimeReviver, loadFromLocalstorage, setLocalstorage } from '$lib/utils';
import { derived, get, writable, type Writable } from 'svelte/store';
import { fetchApi } from './common-store';

interface ICriteria {
	after?: Date;
	before?: Date;
	sortBy: 'date_taken' | 'date_uploaded' | 'date_updated';
	sortDescending: boolean;
}

async function getPhotos(
	page: number,
	pagesize: number,
	criteria: ICriteria | undefined = undefined
): Promise<PaginatedResults<Photo> | null> {
	if (page < 1) {
		return null;
	}
	const offset = (page - 1) * pagesize;

	const urlParams = new URLSearchParams({
		offset: `${offset}`,
		limit: `${pagesize}`
	});
	if (criteria) {
		if (criteria.after) {
			urlParams.append('after', dateFormat(criteria.after).toSQLDate());
		}
		if (criteria.before) {
			urlParams.append('before', dateFormat(criteria.before).toSQLDate());
		}
		if (criteria.sortBy) {
			urlParams.append('sortBy', criteria.sortBy);
		}
		if (criteria.sortDescending) {
			urlParams.append('sortDescending', criteria.sortDescending ? 'True' : 'False');
		}
	}
	const url = `/api/images/?${urlParams.toString()}`;
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
const criteria = writable({ sortBy: 'date_taken', sortDescending: false } as ICriteria);
//debounce?
let fetchTimerId: any = undefined;
async function refreshItems(_page: number, _pagesize: number, _criteria: ICriteria) {
	const result = await getPhotos(_page, _pagesize, _criteria);
	if (result) {
		itemList.set(result.items);
		if (result.total_count) {
			totalItems.set(result.total_count);
		}
	}
}
const changes = derived(
	[currentPage, numPerPage, criteria],
	([CurrentPage, NumPerPage, Criteria]) => {
		if (fetchTimerId) {
			console.log('debounce');
			clearTimeout(fetchTimerId);
		}
		fetchTimerId = setTimeout(() => refreshItems(CurrentPage, NumPerPage, Criteria), 50);
	}
);
changes.subscribe((x) => console.log('changed'));

export const photopages = {
	items: derived(itemList, (_) => _),
	numPerPage,
	currentPage,
	totalItems,
	criteria,
	refresh: async () => await refreshItems(get(currentPage), get(numPerPage), get(criteria))
};
// load the first page
currentPage.set(1);

export async function savePhoto(id: number, photo: Partial<Photo>) {
	console.log('saving photo', photo);
	const response = await fetchApi(`/api/images/${id}`, {
		method: 'PATCH',
		body: JSON.stringify(photo),
		headers: {
			'Content-Type': 'application/json'
		}
	});
	if (response) {
		const result: Photo = JSON.parse(response, dateTimeReviver);
		itemList.update((items) => items.map((itm) => (itm.id === result.id ? result : itm)));
	}
	console.log('save response', response);
}
