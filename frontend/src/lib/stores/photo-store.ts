import type { PaginatedResults } from '$lib/models/paginated-results';
import type { Photo } from '$lib/models/photo';
import { dateFormat, dateTimeReviver, loadFromLocalstorage, setLocalstorage } from '$lib/utils';
import { derived, get, writable, type Writable } from 'svelte/store';
import { fetchApi } from './common-store';
import { PaginatedStore } from '$lib/models/paginated-store';
import { tick } from 'svelte';

export interface ICriteria {
	q?: string;
	person_ids?: number[];
	after?: Date;
	before?: Date;
	sortBy: 'date_taken' | 'date_uploaded' | 'date_updated';
	sortDescending: boolean;
}
export const photoCriteria = writable({ sortBy: 'date_taken', sortDescending: false } as ICriteria);
export const paginatedPhotos = new PaginatedStore<Photo>(async (offset: number, limit: number) => {
	const urlParams = new URLSearchParams({
		offset: `${offset}`,
		limit: `${limit}`
	});
	const criteria = get(photoCriteria);
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
	const response = await fetchApi(url, {
		headers: { accept: 'application/json' }
	});
	const result: PaginatedResults<Photo> = await JSON.parse(response || '[]', dateTimeReviver);
	// console.log(`getPhotos`, result);
	return result;
});
photoCriteria.subscribe((C) => {
	console.log(C, get(paginatedPhotos.currentPage));
	if (get(paginatedPhotos.currentPage) != 1) {
		console.log('setting page to 1');
		tick().then(() => {
			paginatedPhotos.setCurrentPage(1);
		});
	} else {
		paginatedPhotos.refresh();
	}
});

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
		paginatedPhotos.refresh();
	}
	console.log('save response', response);
}
