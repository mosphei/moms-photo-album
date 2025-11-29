console.log('sq.js');
self.addEventListener('fetch', function(event) {
  // Check if the request is for your API or protected resources
  //if (event.request.url.includes('/api')) {
    event.respondWith(
      customHeaderRequestFetch(event)
    );
  //}
});

function customHeaderRequestFetch(event) {
    // Retrieve your token (e.g., from IndexedDB using a library like idb-keyval)
    let token = "YOUR_AUTH_TOKEN_HERE"; // This value should be retrieved dynamically

    // Copy existing headers
    const headers = new Headers(event.request.headers);
    try {
        if (localStorage.token) {
            const token = JSON.parse(localStorage.token).access_token;
            headers = {
                Authorization: `Bearer ${token}`,
                mode: 'CORS'
            };
            console.log(`token=${token}`);
            headers.set('Authorization', `Bearer ${token}`);
            return fetch(r);
        } else { console.log("no token")}
    } catch {
        localStorage.removeItem('token');
    }
  // Create a new request object with the custom headers and the 'cors' mode
  const newRequest = new Request(event.request, {
    headers: headers,
    mode: 'cors', // Important for custom headers
    credentials: 'omit' // Adjust as needed based on your cookie policy
  });
  return fetch(newRequest);
}
