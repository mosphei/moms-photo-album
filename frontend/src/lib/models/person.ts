export interface Person {
	id: number;
	name: string;
	past_names?: string;
	photo_count?: number;
}
type searchPerson = Person & { relevance: number };
