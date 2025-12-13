import type { Person } from './person';
import { type SizeEnum, MEDIAPATH } from './settings';

export interface Photo {
	id: number;
	filename: string;
	description: string;
	date_taken: Date;
	size: number;
	content_type: string;
	people: Person[];
}

export interface PhotoUpdate {
	filename?: string;
	description?: string;
	date_taken?: Date;
	people?: Person[];
	rotation?: number;
}

export function photoPath(size: SizeEnum, photo: Photo) {
	const filename = photo.filename || `${photo.id}_${size}.jpg`;
	return `${MEDIAPATH}/${size}/${photo.id}/${filename}`;
}
