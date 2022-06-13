import { writable } from "svelte/store";

const default_space = {
  space_name: "products",
  backend: "http://localhost:8282",
};
let local;

if (!localStorage.getItem("active_space")) {
  localStorage.setItem("active_space", JSON.stringify(default_space));
}

local = JSON.parse(localStorage.getItem("active_space"));

const { subscribe, set } = writable(local);

function customSet(spacename) {
  set(spacename);
  localStorage.setItem("active_space", JSON.stringify(spacename));
}

export const active_space = {
  set: (value) => customSet(value),
  subscribe,
  reset: () => customSet(default_space),
};
