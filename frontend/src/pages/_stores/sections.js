import { writable } from "svelte/store";
import initial_sections from './sections.json';

export const sections =  writable(initial_sections);
