import type { Photo } from "$lib/models/photo";
import { dateTimeReviver } from "$lib/utils";
import { createFetcher, createStore, fetchApi } from "./common-store";

const data:Photo[] = [];

export async function getPhotos(page: number, pagesize: number):Promise<Photo[]> {
    const skip = page * pagesize;
    const url = `/api/images/?skip=${skip}&limit=${pagesize}`;
    console.log(`url:${url}`);
    const response = await fetchApi(url,{
        headers:{accept: 'application/json'}
    });
    const result = await JSON.parse(response||'[]',dateTimeReviver);
    console.log(`getPhotos`, result);
    return result;
}