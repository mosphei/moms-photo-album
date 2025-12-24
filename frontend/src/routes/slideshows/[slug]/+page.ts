import type { PageLoad } from './$types';
export const load: PageLoad = ({ params }) => {
	let id = parseInt(params.slug);
	if (isNaN(id)) {
		id = 0;
	}
	return {
		id
	};
};
