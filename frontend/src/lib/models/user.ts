import type { Person } from './person';

export interface User {
	id: number;
	username: string;
	admin: boolean;
	person?: Person;
}

export interface UserCreate {
	username: string;
	password: string;
}
