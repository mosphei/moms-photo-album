const SizeKeys = ['t', 'm', 'l', 'o'] as const;
export type SizeEnum = (typeof SizeKeys)[number];
export const IMAGESIZES: { [K in SizeEnum]: number[] } = {
	t: [400, 400],
	m: [1280, 720],
	l: [1921, 1280],
	o: []
};
export const MEDIAPATH = '/api/images/files';
