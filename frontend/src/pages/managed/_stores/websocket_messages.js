import {website} from "../../../space_config";
import {writable} from "svelte/store";

const url = `${website.backend.replace(/^http/, "ws")}/terminal`

const messages = writable([]);

let websocket = null;

const retry_wait = 3000;
let retries_count = 0;
let timer_is_set = false;

function connect() {
  if(null === websocket || websocket.readyState === 3) {
    retries_count++;
    websocket = new WebSocket(url);
    websocket.onopen = function () {retries_count = 0;};
    websocket.onerror = function () {retry(); console.log("WS err reconn");};
    websocket.onclose = function () {retry(); console.log("WS cls reconn");};
    websocket.onmessage = function (event) {messages.update((old) => { return [...old, event.data.trim()]; });};
  }
}

// Called by the timer.
function reconnect() {
  if(null === websocket || websocket.readyState === 3) {
    connect();
  }
  timer_is_set = false;
}

// Called when we need to reconnect
function retry() {
  if(!timer_is_set && (null === websocket || websocket.readyState === 3)) {
    websocket = null;
    timer_is_set = true;
    setTimeout(reconnect, retry_wait * (1+retries_count));
  }
}

connect();

export default {
	subscribe: messages.subscribe,
  send:(message) => {
    if(websocket) {
      if( websocket.readyState === WebSocket.OPEN) {
          websocket.send(message);
      } else if(websocket.readyState === WebSocket.CLOSED) {
        console.log("WS cls2 reconn");
        retry();
      } 
      // FIXME : we should notify the user that the connection was lost.
    } else {
      console.log("Web socket not connected");
      retry();
    }
  }
}

