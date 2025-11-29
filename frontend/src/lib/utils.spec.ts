import { expect, test } from 'vitest';
import { rangeAroundCenter } from './utils';

test('rangeAroundCenter', () => {
	// 1,2,3,4,5,6,7,8,9,10
	const r1 = rangeAroundCenter(5, 3, 10);
	expect(r1).toEqual([4, 5, 6]);
	expect(rangeAroundCenter(10, 3, 10)).toEqual([8, 9, 10]);
	expect(rangeAroundCenter(1, 3, 10)).toEqual([1, 2, 3]);
	// larger
	expect(rangeAroundCenter(5, 5, 10)).toEqual([3, 4, 5, 6, 7]);
	expect(rangeAroundCenter(2, 5, 3)).toEqual([1, 2, 3]);
	// undefined total
	expect(rangeAroundCenter(1, 3)).toEqual([1, 2]);
});
