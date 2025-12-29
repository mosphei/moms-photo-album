import { derived, get, writable, type Writable } from 'svelte/store';
import type { PaginatedResults } from './paginated-results';

export class PaginatedStore<TData = any, TCriteria = any> {
	private data: (TData | null)[] = [];
	private current_page = writable(1);
	private limit = writable(10);
	private offset = derived([this.current_page, this.limit], ([P, L]) => {
		return (P - 1) * L;
	});
	private items = writable([] as TData[]);
	public currentItems = derived(this.items, (ITEMS) => ITEMS);
	private total_items = writable(-1);
	public totalCount = derived(this.total_items, (TI) => (TI < 0 ? undefined : TI));
	public criteria = writable(undefined as TCriteria | undefined);
	fetcher: (
		offset: number,
		limit: number,
		criteria: TCriteria | undefined
	) => Promise<PaginatedResults<TData>>;
	async fetchAndApply(offset: number, limit: number, criteria: TCriteria | undefined) {
		const paginated = await this.fetcher(offset, limit, criteria);
		if (paginated?.items) {
			console.log(paginated);
			if (paginated.total_count !== undefined && paginated.total_count != this.data.length) {
				this.total_items.set(paginated.total_count);
				const newArray = Array.from({ length: paginated.total_count }).map(
					(x, i) => this.data[i] || null
				);
				this.data = newArray;
			}
			console.log(`${paginated.offset}, ${paginated.items.length}`, paginated.items);
			this.data.splice(paginated.offset, paginated.items.length, ...paginated.items);
			console.log(this.data);
		}
	}
	async refresh() {
		const offset = get(this.offset);
		const limit = get(this.limit);
		const criteria = get(this.criteria);
		await this.fetchAndApply(offset, limit * 2, criteria);
		const x = this.data.slice(offset, offset + limit).filter((v) => v != null);
		console.log(x);
		this.items.set(x);
	}
	lastPage = derived([this.limit, this.total_items], ([LIMIT, TOTAL]) => {
		if (TOTAL >= 0 && LIMIT > 0) {
			return Math.ceil(TOTAL / LIMIT);
		}
		return 1;
	});

	async setCurrentPage(page: number) {
		this.current_page.set(page);
		const offset = get(this.offset);
		const limit = get(this.limit);
		const values = this.data.slice(offset, offset + limit);
		const safeValues = values.filter((v) => v !== null);
		if (safeValues.length == values.length) {
			console.log('cached items');
			this.items.set(safeValues);
		} else {
			await this.refresh();
		}
		const nextvalues = this.data.slice(offset + limit, offset + limit * 2);
		if (nextvalues.some((v) => v === null)) {
			// don't wait for this to complete
			this.fetchAndApply(offset + limit, offset + limit * 2, get(this.criteria));
		}
	}
	public currentPage = derived(this.current_page, (P) => P);
	async setNumPerPage(numPerPage: number) {
		if (numPerPage < 1) {
			throw new Error('invalid operation');
		}
		// what page should we be on?
		const currentOffset = get(this.offset);
		const newPage = Math.floor(currentOffset / numPerPage) + 1;
		this.limit.set(numPerPage);
		return this.setCurrentPage(newPage);
	}
	public numPerPage = derived(this.limit, (N) => N);
	async prevPage() {
		return this.setCurrentPage(get(this.current_page) - 1);
	}
	async nextPage() {
		return this.setCurrentPage(get(this.current_page) + 1);
	}
	async getItem(i: number) {
		if (this.data[i] === null) {
			await this.fetchAndApply(i, get(this.limit), get(this.criteria));
		}
		return this.data[i];
	}
	constructor(fetcher: typeof this.fetcher) {
		this.fetcher = fetcher;
		this.criteria.subscribe((C) => {
			this.setCurrentPage(1);
		});
	}
}
