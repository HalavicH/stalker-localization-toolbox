// store.js
import {type Writable, writable} from 'svelte/store';

export const status: Writable<string> = writable("Status bar");

// Details overlay
export enum DetailsMode {
    LinkDetails,
    NodeDetails
}

export interface LinkDetails {
    sourceFilePath: string,
    targetFilePath: string,
    duplicatedKeyDivs: string[],
    duplicatedKeysCnt: number,
}

export interface NodeDetails {
    filePath: string,
    allKeysAsDivList: string,
    keysCnt: number,
}

export interface DetailsData {
    mode: DetailsMode,
    data: NodeDetails | LinkDetails,
}

export const details: Writable<DetailsData> = writable();

// Tooltip
export interface TooltipState {
    posX: number,
    posY: number,
    html: string,
    visible: boolean
}

export const tooltip: Writable<Partial<TooltipState>> = writable();
