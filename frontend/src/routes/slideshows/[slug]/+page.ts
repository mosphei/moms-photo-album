import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
export const load: PageLoad = async ({ params }) => {
	let id = parseInt(params.slug);
	if (isNaN(id)) {
		error(404);
	}
	return {
		id
	};
};
