import { derived, get, writable, type Writable } from 'svelte/store';
import type { PaginatedResults } from './paginated-results';

export class PaginatedStore<T> {
	private current_page = writable(1);
	private limit = writable(10);
	private offset = derived([this.current_page, this.limit], ([P, L]) => {
		return (P - 1) * L;
	});
	private items = writable([] as T[]);
	public currentItems = derived(this.items, (ITEMS) => ITEMS);
	private total_items = writable(-1);
	public totalCount = derived(this.total_items, (TI) => (TI < 0 ? undefined : TI));
	fetcher: (offset: number, limit: number) => Promise<PaginatedResults<T>>;
	async refresh() {
		const paginated = await this.fetcher(get(this.current_page), get(this.limit));
		this.items.set(paginated.items);
		if (paginated.total_count !== undefined) {
			this.total_items.set(paginated.total_count);
		}
	}
	lastPage = derived([this.limit, this.total_items], ([LIMIT, TOTAL]) => {
		if (TOTAL >= 0 && LIMIT > 0) {
			return Math.ceil(TOTAL / LIMIT);
		}
		return 1;
	});
	async setCurrentPage(page: number) {
		this.current_page.set(page);
		return this.refresh();
	}
	public currentPage = derived(this.current_page, (P) => P);
	async setNumPerPage(numPerPage: number) {
		if (numPerPage < 1) {
			throw new Error('invalid operation');
		}
		this.limit.set(numPerPage);
		return this.refresh();
	}
	public numPerPage = derived(this.limit, (N) => N);
	async prevPage() {
		return this.setCurrentPage(get(this.current_page) - 1);
	}
	async nextPage() {
		return this.setCurrentPage(get(this.current_page) + 1);
	}
	constructor(fetcher: typeof this.fetcher) {
		this.fetcher = fetcher;
	}
}
