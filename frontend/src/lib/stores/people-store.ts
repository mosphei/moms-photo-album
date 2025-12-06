import type { PaginatedResults } from "$lib/models/paginated-results";
import type { Person } from "$lib/models/person";
import { dateFormat, dateTimeReviver, loadFromLocalstorage, setLocalstorage } from "$lib/utils";
import { derived, get, writable } from "svelte/store";
import { fetchApi } from "./common-store";

const itemList = writable([] as Person[]);
const initialNumPerPage = loadFromLocalstorage('numPerPage') || '10';
const numPerPage = writable(parseInt(initialNumPerPage));
numPerPage.subscribe((n) => setLocalstorage('numPerPage', n));
const currentPage = writable(1);
const totalItems = writable(null as null | number);
const criteria = writable({ sortBy: 'name', sortDescending: false } as ICriteria);

export interface ICriteria {
	sortBy: 'name';
	sortDescending: boolean;
}

async function getPeople(
    page: number,
    pagesize: number,
    criteria: ICriteria | undefined = undefined
): Promise<PaginatedResults<Person> | null> {
    // console.log('getPeople');
    if (page < 1) {
        return null;
    }
    const offset = (page - 1) * pagesize;

    const urlParams = new URLSearchParams({
        offset: `${offset}`,
        limit: `${pagesize}`
    });
    if (criteria) {
        if (criteria.sortBy) {
            urlParams.append('sortBy', criteria.sortBy);
        }
        if (criteria.sortDescending) {
            urlParams.append('sortDescending', criteria.sortDescending ? 'True' : 'False');
        }
    }
    const url = `/api/people/?${urlParams.toString()}`;
    console.log(`url:${url}`);
    const response = await fetchApi(url, {
        headers: { accept: 'application/json' }
    });
    const result: PaginatedResults<Person> = await JSON.parse(response || '[]', dateTimeReviver);
    console.log(`getPeople`, result);
    return result;
}

async function refreshItems(_page: number, _pagesize: number, _criteria: ICriteria) {
    // console.log(`refresh(${_page},${_pagesize},${_criteria.sortBy})`)
    const result = await getPeople(_page, _pagesize, _criteria);
    if (result) {
        itemList.set(result.items);
        if (result.total_count) {
            totalItems.set(result.total_count);
        }
    } else {
        console.log('no results!');
    }
}

let fetchTimerId: any = undefined;
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

export const peoplepages = {
    items: derived(itemList, (_) => _),
    numPerPage,
    currentPage,
    totalItems,
    criteria,
    refresh: async () => await refreshItems(get(currentPage), get(numPerPage), get(criteria))
};

// fetch at least once
setTimeout(()=>peoplepages.refresh,10);