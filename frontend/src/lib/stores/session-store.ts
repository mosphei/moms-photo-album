import { browser } from "$app/environment";
import { derived, writable } from "svelte/store";

export interface TokenResponse {
    access_token: string;
    token_type: string;
}
interface ISession {
    setToken:(token:string|undefined) => void;
    loggedIn: boolean|undefined;
}
function getInitialToken():TokenResponse|null {
    if (browser) {
        try {
            if (localStorage.token) {
                return JSON.parse(localStorage.token);
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

export const session = {
    token: derived(TOKEN,x=>x),
    loggedIn:derived(TOKEN, x => x !== null),
    setToken:(token: TokenResponse) => {
        localStorage.setItem('token',JSON.stringify(token));
        TOKEN.set(token);
    },
    clearToken: () => {
        localStorage.removeItem('token');
        TOKEN.set(null);
    }
};