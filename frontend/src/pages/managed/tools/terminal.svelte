<script>
  //import { AttachAddon } from 'xterm-addon-attach';
  import { FitAddon } from "xterm-addon-fit";
  import { WebLinksAddon } from "xterm-addon-web-links";
  //import { SearchAddon } from 'xterm-addon-search';
  import { Terminal } from "xterm";
  //import LocalEchoController from 'local-echo';
  import { onMount } from "svelte";

  export let scoped = {};
  scoped;
  export let scopedSync = {};
  scopedSync;

  let container;
  //const websocket = new WebSocket('ws://localhost:4000/terminal');
  //websocket.addEventListener('open', (e) => console.log(e));
  //websocket.addEventListener('message', (e) => console.log(e));

  const terminal = new Terminal({
    theme: { background: "#2c2c54", white: "#706fd3" },
    fontSize: 14,
    fontFamily: "monospace",
    cursorBlink: true,
    convertEol: true,
    useStyle: true,
    disableStdin: false,
  });

  // { cursorBlink: true, cursorStyle: 'underline', allowTransparency: true}); //,  convertEol: true, useStyle: true });
  const fitAddon = new FitAddon();
  terminal.loadAddon(new WebLinksAddon());
  //terminal.loadAddon(new SearchAddon());
  terminal.loadAddon(fitAddon);
  //const localEcho = new LocalEchoController();
  //terminal.loadAddon(localEcho);

  terminal.prompt = () => {
    terminal.write("\r\n > ");
  };

  let command = "";

  terminal.onKey((e) => {
    // : { key: string, domEvent: KeyboardEvent }
    const ev = e.domEvent;
    const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey;
    //console.log(ev);

    if (ev.keyCode === 13) {
      console.log("Command : ", command);
      if ("clear" === command) {
        terminal.clear();
      } else if ("help" === command) {
        terminal.write("\r\n   Help goes here ...");
      }
      command = "";
      terminal.prompt();
      terminal.write(command);
    } else if (ev.keyCode === 38 || ev.keyCode === 40) {
      // Up and Down keys TBD navigate history
    } else if (ev.keyCode === 37) {
      if (terminal._core.buffer.x > 3) {
        terminal.write(e.key);
      }
    } else if (ev.keyCode === 39) {
      if (terminal._core.buffer.x < 3 + command.length) {
        terminal.write(e.key);
      }
    } else if (ev.keyCode === 8) {
      // Do not delete the prompt
      if (terminal._core.buffer.x > 3 && command.length > 0) {
        terminal.write("\b \b");
        //terminal.write('CSI Ps X');
        console.log(command, command.length, terminal._core.buffer.x);
        command =
          command.slice(0, terminal._core.buffer.x - 4) + command.slice(terminal._core.buffer.x - 3, command.length);
        //console.log(command);
      }
    } else if (printable) {
      command += e.key;
      terminal.write(e.key);
    }
  });

  onMount(async () => {
    //const attachAddon = new AttachAddon(websocket);
    //terminal.loadAddon(attachAddon);

    terminal.open(container);
    //terminal.write('Hello from \x1B[1;3;31mxterm.js\x1B[0m $');
    fitAddon.fit();
    //terminal.writeln('Welcome to xterm.js');
    terminal.writeln("This is a local terminal emulation, without a real terminal in the back-end.");
    //terminal.writeln('Type some keys and commands to play around.');
    terminal.writeln('type "help" for help.');
    terminal.prompt();
    // Terminal.applyAddon(attach);
    // term.attach($results_socket, true, true);
    //localEcho.read(" > ").then(input => console.log("User entered:", input))
    //.catch(error => console.log("Error reading:", error));
  });
</script>

<div id="terminal" bind:this="{container}" class="h-100"></div>

<style global>
  @import "xterm/css/xterm.css";
</style>
