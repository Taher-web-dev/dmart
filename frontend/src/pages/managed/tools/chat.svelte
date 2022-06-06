<script>
  import websocket from "../_stores/websocket_messages.js";

  export let scopedSync = {};
  scopedSync;
  export let scoped = {};
  scoped;

  let line = "";
  function send() {
    websocket.send(line);
    line = "";
  }

  $: disabled = line.length == 0;

  function keyup(event) {
    if (event.keyCode === 13 && line.length > 0) {
      send();
    }
  }
</script>

<h3>Chat</h3>
<input type="text" bind:value="{line}" on:keyup|preventDefault="{keyup}" /><button
  on:click|preventDefault="{send}"
  disabled="{disabled}">Send</button>
<p>
  {#each $websocket as message}
    {message}<br />
  {/each}
</p>
