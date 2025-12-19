import type { PaginatedResults } from '$lib/models/paginated-results';
import type { Person } from '$lib/models/person';
import { dateFormat, dateTimeReviver, loadFromLocalstorage, setLocalstorage } from '$lib/utils';
import { derived, get, writable } from 'svelte/store';
import { fetchApi } from './common-store';
import { PaginatedStore } from '$lib/models/paginated-store';
import { errorAlert } from '$lib/alerts';
import { tick } from 'svelte';

export interface IPeopleCriteria {
	q?: string;
	sortBy: 'name';
	sortDescending: boolean;
}
export const peopleCriteria = writable({
	sortBy: 'name',
	sortDescending: false
} as IPeopleCriteria);
export const peopleStore = new PaginatedStore<Person>(async (offset: number, limit: number) => {
	const urlParams = new URLSearchParams({
		offset: `${offset}`,
		limit: `${limit}`
	});
	const criteria = get(peopleCriteria);
	if (criteria.q) {
		urlParams.append('q', criteria.q);
	}
	if (criteria.sortBy) {
		urlParams.append('sortBy', criteria.sortBy);
	}
	if (criteria.sortDescending) {
		urlParams.append('sortDescending', criteria.sortDescending ? 'True' : 'False');
	}
	try {
		const url = `/api/people/?${urlParams.toString()}`;
		console.log(`url:${url}`);
		const response = await fetchApi(url, {
			headers: { accept: 'application/json' }
		});
		const result: PaginatedResults<Person> = await JSON.parse(response || '[]', dateTimeReviver);
		console.log(`getPeople`, result);
		return result;
	} catch (error) {
		errorAlert(`unable to get people list`, error, 5000);
		return { items: [], total_count: 0, offset, limit };
	}
});

// go back to page 1 if criteria change
peopleCriteria.subscribe((C) => {
	console.log(C, get(peopleStore.currentPage));
	if (get(peopleStore.currentPage) != 1) {
		console.log('setting page to 1');
		tick().then(() => {
			peopleStore.setCurrentPage(1);
		});
	} else {
		peopleStore.refresh();
	}
});

export async function savePerson(person: Person) {
	console.log('saving person', person);
	const response = await fetchApi(`/api/people/${person.id}`, {
		method: 'PATCH',
		body: JSON.stringify(person),
		headers: {
			'Content-Type': 'application/json'
		}
	});
	if (response) {
		const result: Person = JSON.parse(response, dateTimeReviver);
		peopleStore.refresh();
	}
	console.log('save response', response);
}
