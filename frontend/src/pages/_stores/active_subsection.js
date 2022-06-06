import { writable } from 'svelte/store';

let initial = {path:[], id: "", displayname: ""};

export const active_subsection = writable(initial);
