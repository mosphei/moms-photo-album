import { browser } from '$app/environment';

/** applies nested properties in operand to target
 * overwrites existing target properties
 * does mutate target, if you dont want target mutated
 * pass {} as first parameter
 */
export function deepMerge(target: any, ...operands: any[]) {
	// Iterate over the keys in each source object
	operands.forEach((operand) => {
		for (const key in operand) {
			// Check if the key exists directly on the source object (not inherited)
			if (Object.prototype.hasOwnProperty.call(operand, key)) {
				// If both target and source have the key and both values are objects,
				// recursively merge them.
				if (
					typeof target[key] === 'object' &&
					target[key] !== null &&
					typeof operand[key] === 'object' &&
					operand[key] !== null &&
					!Array.isArray(target[key]) && // Ensure they are plain objects, not arrays
					!Array.isArray(operand[key])
				) {
					target[key] = deepMerge(target[key], operand[key]);
				} else {
					// Otherwise, directly assign the source property to the target
					target[key] = operand[key];
				}
			}
		}
	});
	return target;
}

/** use to parse dates from JSON as Date and not string
 *  JSON.parse(txt, dateTimeReviver);
 * assumes time zone built in to date string
 * e.g. 2024-08-08T08:55:36-07:00
 */
export function dateTimeReviver(key: string, value: any) {
	if (typeof value == 'string' && /\d{4}-\d{2}-\d{2}[ T]\d\d:\d\d:\d\d/.test(value)) {
		// it's a date
		return new Date(value);
	}
	return value;
}
/** use to center a page in a button range */
export function rangeAroundCenter(center: number, width: number, max?: number) {
	let retval: number[] = [center];
	let start = center - Math.floor(width / 2);
	if (start < 1) {
		start = 1;
	}
	let end = start + width - 1;
	if (!max) {
		max = center + 1;
	}
	if (end > max) {
		end = max;
		start = end - width + 1;
		if (start < 1) {
			start = 1;
		}
	}

	const length = end - start + 1;
	return Array.from({ length: length }, (_, index) => start + index);
}

export function loadFromLocalstorage(key: string): string | null {
	if (browser) {
		return localStorage?.getItem('mpdb' + key);
	}
	return null;
}
export function setLocalstorage(key: string, value: any) {
	if (browser) {
		localStorage.setItem('mpdb' + key, JSON.stringify(value));
	}
}

export function dateFormat(date: Date) {
	function toTime() {
		return date.toTimeString().substring(0, 5);
	}
	function toDate() {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}
	return {
		toSQLTime: toTime,
		toSQLDate: toDate,
		toSQLDateTime: () => `${toDate()} ${toTime()}`
	};
}
