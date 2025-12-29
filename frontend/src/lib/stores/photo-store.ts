import type { PaginatedResults } from '$lib/models/paginated-results';
import type { Photo } from '$lib/models/photo';
import { dateFormat, dateTimeReviver, loadFromLocalstorage, setLocalstorage } from '$lib/utils';
import { derived, get, writable, type Writable } from 'svelte/store';
import { fetchApi } from './common-store';
import { PaginatedStore } from '$lib/models/paginated-store';
import { tick } from 'svelte';
import { errorAlert } from '$lib/alerts';

export interface IPhotoCriteria {
	q?: string;
	person_ids?: number[];
	after?: Date;
	before?: Date;
	sortBy: 'date_taken' | 'date_uploaded' | 'date_updated';
	sortDescending: boolean;
} /*
export const photoCriteria = writable({
	sortBy: 'date_taken',
	sortDescending: false
} as IPhotoCriteria);*/
const emptyResult: PaginatedResults<Photo> = {
	items: [],
	offset: 0,
	limit: 0,
	total_count: 0
};
async function fetchPhotos(offset: number, limit: number, criteria: IPhotoCriteria | undefined) {
	const urlParams = new URLSearchParams({
		offset: `${offset}`,
		limit: `${limit}`
	});
	if (criteria) {
		if (criteria.q && criteria.q.length > 2) {
			urlParams.append('q', criteria.q);
		}
		if (criteria.person_ids && criteria.person_ids.length) {
			criteria.person_ids.forEach((id) => urlParams.append('person_id', id.toString()));
		}
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
	try {
		const response = await fetchApi(url, {
			headers: { accept: 'application/json' }
		});
		const result: PaginatedResults<Photo> = response
			? JSON.parse(response, dateTimeReviver)
			: emptyResult;
		console.log(`getPhotos`, result);
		return result;
	} catch (error) {
		errorAlert(`unable to get photos`, error, 10000);
	}
	return {
		items: [],
		offset,
		limit,
		total_count: 0
	};
}
export const photoStore = new PaginatedStore<Photo, IPhotoCriteria>(fetchPhotos);
// go back to page 1 if criteria change
/*photoCriteria.subscribe((C) => {
	console.log(C, get(photoStore.currentPage));
	if (get(photoStore.currentPage) != 1) {
		console.log('setting page to 1');
		tick().then(() => {
			photoStore.setCurrentPage(1);
		});
	} else {
		photoStore.refresh();
	}
}); */

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
		// itemList.update((items) => items.map((itm) => (itm.id === result.id ? result : itm)));
		photoStore.refresh();
	}
	console.log('save response', response);
}
