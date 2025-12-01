import { type SizeEnum, MEDIAPATH } from './settings';

export interface Photo {
	id: number;
	filename: string;
	description: string;
	date_taken: Date;
	people: string[];
}

export function photoPath(size: SizeEnum, photo: Photo) {
	const filename = photo.filename || `${photo.id}_${size}.jpg`;
	return `${MEDIAPATH}/${size}/${photo.id}/${filename}`;
}
