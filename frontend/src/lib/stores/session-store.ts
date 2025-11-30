import { browser } from '$app/environment';
import { derived, writable } from 'svelte/store';

export interface TokenResponse {
	access_token: string;
	token_type: string;
}
interface ISession {
	setToken: (token: string | undefined) => void;
	loggedIn: boolean | undefined;
}
let postToken:((token: string)=>void)|undefined = undefined;
/* initialize the serviceworker */
if (browser ) {
	if ( 'serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');

  // Wait until the service worker is active/ready
  navigator.serviceWorker.ready.then((registration) => {
	console.log('sw ready');
	postToken = (authToken) => {
		if (authToken && registration.active) {
			console.log('seding');
			// Send the token to the active service worker
			registration.active.postMessage({
				type: 'SET_AUTH_TOKEN',
				token: authToken
			});
		}
	};

    
  });
}
}
let timerId:any = 0;
function waitForPostToken(token: string) {
	if (timerId) {
		clearTimeout(timerId);
	}
	if (postToken) {
		postToken(token);
	} else {
		console.log('no sw!');
		timerId = setTimeout(()=>waitForPostToken(token), 300);
	}
}
function getInitialToken(): TokenResponse | null {
	if (browser) {
		try {
			if (localStorage.token) {			
				const tkn:TokenResponse = JSON.parse(localStorage.token);
				waitForPostToken(tkn.access_token);
				return tkn;
			}
		} catch {
			localStorage.removeItem('token');
		}
	}
	return null;
}
const initialToken = getInitialToken();
console.log('initialToken', initialToken);
const TOKEN = writable(initialToken);
TOKEN.subscribe(t=>t&&waitForPostToken(t.access_token));
export const session = {
	token: derived(TOKEN, (x) => x),
	loggedIn: derived(TOKEN, (x) => x !== null),
	setToken: (token: TokenResponse) => {
		localStorage.setItem('token', JSON.stringify(token));
		TOKEN.set(token);
	},
	clearToken: () => {
		localStorage.removeItem('token');
		TOKEN.set(null);
	}
};
