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
	progressCallback: (e: any) => void
) {
	return new Promise((resolve, reject) => {
		const xhr = new XMLHttpRequest();

		xhr.upload.addEventListener(
			'progress',
			(event) => {
				if (event.lengthComputable) {
					const percentComplete = (event.loaded / event.total) * 100;
					progressCallback(percentComplete);
				}
			},
			false
		);

		xhr.addEventListener('load', () => resolve(xhr.response), false);
		xhr.addEventListener('error', () => reject(new Error('Upload failed')), false);
		xhr.addEventListener('abort', () => reject(new Error('Upload aborted')), false);

		xhr.open('POST', url, true);
		xhr.send(file);
	});
}
