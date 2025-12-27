import type { Photo } from './photo';

export interface Slideshow {
	id: number;
	title: string;
	slide_count: number;
}

export interface SlideshowUpdate {
	id: number;
	title: string;
	slides: number[];
}
