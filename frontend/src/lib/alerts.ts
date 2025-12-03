import { toast, type SvelteToastOptions } from '@zerodevx/svelte-toast';
/** duration of 0 will not auto disappear */
export const successAlert = (message: string, duration = 3000) => {
	const id = toast.push(message, {
		theme: {
			'--toastColor': '#ffffff',
			'--toastBackground': 'var(--bs-success,red)',
			'--toastBarBackground': 'var(--bs-success-bg-subtle)'
		},
		initial: 1,
		duration
	});
	setTimeout(() => toast.pop(id), duration);
	return {
		id,
		dismiss: () => toast.pop(id)
	};
};
export const progressAlert = (msg = 'Please wait...', opts: SvelteToastOptions = {}) => {
	let initial = 0;
	let next = 0.4;
	let duration = 500;
	const id = toast.push(msg, {
		duration,
		initial,
		next,
		...opts
	});
	// after 1 second another .4
	let timerid = setInterval(() => {
		next = (0.8 + next) / 2;
		toast.set(id, { next });
	}, duration);
	return {
		id,
		dismiss: () => {
			clearInterval(timerid);
			toast.pop(id);
		}
	};
};
function getErrorDetails(err: any) {
	let detail = '';
	if (err) {
		// is err a stringified json?
		try {
			err = JSON.parse(err);
		} catch {
			//console.log('nope', err);
		}
		if (err) {
			detail += ` ${err.ExceptionMessage || err.Message || err.message || err.toString()}`;
		}
	}
	return detail;
}
/** duration of zero will not auto remove */
export const errorAlert = (
	msg: string,
	err: unknown,
	duration = 60000,
	opts: SvelteToastOptions = {}
) => {
	const detail = getErrorDetails(err);
	const id = toast.push(`${msg} <code>${detail}</code>`, {
		theme: {
			'--toastColor': '#ffffff',
			'--toastBackground': 'var(--bs-danger,red)',
			'--toastBarBackground': 'var(--bs-danger-bg-subtle)'
		},
		initial: 0,
		duration,
		...opts
	});
	setTimeout(() => toast.pop(id), duration);
	return {
		id,
		dismiss: () => {
			toast.pop(id);
		}
	};
};
