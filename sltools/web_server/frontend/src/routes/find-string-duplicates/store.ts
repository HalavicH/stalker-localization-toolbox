// store.js
import {type Writable, writable} from 'svelte/store';

export const status: Writable<string> = writable("Status bar");
export const details: Writable<string> = writable("Click on any node/link to see the details");

export interface TooltipState {
    posX: number,
    posY: number,
    html: string,
    visible: boolean
}

export const tooltip: Writable<Partial<TooltipState>> = writable();
