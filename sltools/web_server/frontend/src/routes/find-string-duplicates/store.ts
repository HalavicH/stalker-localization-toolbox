// store.js
import {type Writable, writable} from 'svelte/store';

export const status: Writable<string> = writable("Status bar");
export const details: Writable<string> = writable("Click on any node/link to see the details");
export const tooltipData: Writable<string> = writable("");
export const tooltipPos: Writable<string> = writable("");
