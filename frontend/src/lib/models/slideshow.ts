import type { Photo } from './photo';

export interface Slideshow {
	id: number;
	title: string;
	length: number;
	slides: Photo[];
}

export interface SlideshowUpdate {
	id: number;
	title: string;
	slides: number[];
}
