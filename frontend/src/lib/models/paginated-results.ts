export interface PaginatedResults<T> {
	items: T[];
	total_count: number;
	offset: number;
	limit: number;
}
