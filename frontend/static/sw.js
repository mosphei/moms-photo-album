let currentAuthToken = null; // Variable to store the token

// Listen for messages from the main application thread
self.addEventListener('message', (event) => {
  // event.data contains the message payload
  if (event.data && event.data.type === 'SET_AUTH_TOKEN') {
    currentAuthToken = event.data.token;
    console.log('Service Worker received auth token:', currentAuthToken);
  }
});

self.addEventListener('fetch', function (event) {
	// Check if the request is for your API or protected resources
	//if (event.request.url.includes('/api')) {
  if (currentAuthToken) {
	  event.respondWith(customHeaderRequestFetch(event));
	}
});

function customHeaderRequestFetch(event) {
	// Copy existing headers
	const headers = new Headers(event.request.headers);
	headers.set('Authorization', `Bearer ${currentAuthToken}`);
	// Create a new request object with the custom headers and the 'cors' mode
	const newRequest = new Request(event.request, {
		headers: headers,
		mode: 'cors' // Important for custom headers
		// credentials: 'omit' // Adjust as needed based on your cookie policy
	});
	return fetch(newRequest);
}
