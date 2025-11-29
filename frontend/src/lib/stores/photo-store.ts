import type { PaginatedResults } from '$lib/models/paginated-results';
import type { Photo } from '$lib/models/photo';
import { dateTimeReviver } from '$lib/utils';
import { createFetcher, createStore, fetchApi } from './common-store';

const data: Photo[] = [];

export async function getPhotos(page: number, pagesize: number): Promise<PaginatedResults<Photo>> {
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
