import type { PaginatedResults } from '$lib/models/paginated-results';
import { PaginatedStore } from '$lib/models/paginated-store';
import type { Slideshow, SlideshowUpdate } from '$lib/models/slideshow';
import { dateTimeReviver } from '$lib/utils';
import { fetchApi } from './common-store';

interface ICriteria {
	q?: string;
}

async function slideshowFetcher(
	offset: number,
	limit: number,
	criteria: ICriteria | undefined
): Promise<PaginatedResults<Slideshow>> {
	const urlParams = new URLSearchParams({
		offset: `${offset}`,
		limit: `${limit}`
	});
	if (criteria?.q) {
		urlParams.append('q', criteria.q);
	}
	const url = `/api/slideshows/?${urlParams.toString()}`;
	console.log(`url:${url}`);
	const response = await fetchApi(url, {
		headers: { accept: 'application/json' }
	});
	console.log('response', response);
	if (response) {
		const result = JSON.parse(response);
		console.log('slideshow fetcher result', result);
		return result;
	} else {
		return {
			items: [],
			limit,
			offset,
			total_count: 0
		};
	}
}
export const slideshowStore = new PaginatedStore<Slideshow, ICriteria>(slideshowFetcher);
slideshowStore.setNumPerPage(100);
slideshowStore.setCurrentPage(1);

export async function saveSlideshow(slideshow: SlideshowUpdate) {
	let response: string | undefined;
	const body = JSON.stringify(slideshow);
	console.log('body', body);
	if (slideshow.id === 0) {
		// new
		response = await fetchApi('/api/slideshows/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body
		});
	} else {
		response = await fetchApi(`/api/slideshows/${slideshow.id}`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body
		});
	}
	if (response) {
		const result = JSON.parse(response, dateTimeReviver);
		return result;
	}
}
