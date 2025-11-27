/**
 *
 * @param url api endpoint
 * @param file File
 * @param progressCallback will pass percentComplete as parameter
 * Usage:
 * const fileInput = document.getElementById('file-input');
 * const file = fileInput.files[0];
 * uploadFileWithProgress('/upload-endpoint', file, (percent) => {
 *  // Update your progress bar UI with the percentage
 * });
 */
export function uploadFileWithProgress(
	url: string,
	file: File,
	progressCallback: (percentComplete: number) => void,
	headers: any
) {
	return new Promise((resolve, reject) => {
		const xhr = new XMLHttpRequest();
		xhr.upload.addEventListener(
			'progress',
			(event) => {
				if (event.lengthComputable) {
					const percentComplete = Math.floor(event.loaded / event.total) * 99;
					progressCallback(percentComplete);
				}
			},
			false
		);

		xhr.addEventListener(
			'load',
			() => {
				console.log('status', xhr.status);
				if (xhr.status >= 200 && xhr.status < 300) {
					// success
					progressCallback(100);
					resolve(xhr.response);
				} else {
					console.log(`error ${xhr.status} ${xhr.statusText}`)
					progressCallback(0);
					reject(`error ${xhr.status} ${xhr.statusText}`);
				}
			},
			false
		);
		xhr.addEventListener(
			'error',
			(e) => {
				console.log('upload failed', e);
				reject(new Error('Upload failed'));
			},
			false
		);
		xhr.addEventListener(
			'abort',
			(e) => {
				console.log('upload failed', e);
				reject(new Error('Upload aborted'));
			},
			false
		);
		xhr.onerror = function () {
			console.log('Network error.');
		};
		console.log('url:' + url);

		xhr.open('POST', url, true);
		if (headers) {
			Object.entries(headers).forEach(([key, value]) => {
				xhr.setRequestHeader(key, `${value}`);
			});
		}
		const formData = new FormData();
		formData.append('file', file);
		xhr.send(formData);
	});
}
