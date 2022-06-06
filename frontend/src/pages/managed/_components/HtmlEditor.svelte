<script>
  import { onMount } from "svelte";
  import Editor from "cl-editor/dist";
  import { dmart_content } from "../../../dmart";
  import sha1 from "../../../sha1";
  import { Button, Toast, ToastBody, ToastHeader } from "sveltestrap";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let uid = "x";
  export let content;

  let maindiv;
  let editor = null;

  /*
	let changed = false;
  let result;
	let isOpen = false;
	async function update(html) {
		let record = {
			subpath: data.subpath,
			shortname: data.shortname,
			resource_type: data.resource_type,
			attributes: {
				payload: {
					checksum: `sha1:${sha1(html)}`,
					embedded: html,
					content_type: "text/html; charset=utf8",
					bytesize: new Blob([html]).size
				}
			}
		};

		let resp = await dmart_content("update", record);
		result = resp.results[0];
		isOpen = true;
		setTimeout(() => (isOpen = false), 4000);
		console.log("Resp: ", resp.results);
	}*/

  onMount(async () => {
    editor = new Editor({
      target: maindiv,
      props: {
        height: "calc(90%)",
        actions: [
          "viewHtml",
          "undo",
          "redo",
          "b",
          "i",
          //'u',
          //'strike',
          //'sup',
          "sub",
          "h1",
          "h2",
          "p",
          "blockquote",
          "ol",
          "ul",
          "hr",
          "left",
          "right",
          "center",
          "justify",
          "a",
          "image",
          //'forecolor',
          //'backcolor',
          "removeFormat",
          /*{
							name: 'save', // required
							icon: '<svg class="icon blink"><use xlink:href="/symbol-defs.svg#floppy-disk" /></svg>', // string or html string (ex. <svg>...</svg>)
							title: 'Save',
							result: () => {
								if(changed) {
									let html = editor.getHtml(true);
									data.attributes.payload.embedded = html;
									update(html);
									//console.log("Hi there: ", html);
									changed = false;
								}
							}
            }*/
        ],
      },
    });
    editor.setHtml(content, true);
    editor.$on("change", () => {
      content = editor.getHtml(true);
      dispatch("changed");

      // changed = true;
    });
    /*editor.$on('bulr', () => {
			if(changed) {
				content = editor.getHtml(true);
				// data.attributes.payload.embedded = html;
			}
		});*/

    //console.log("H-ID/SN: ", data.shortname, " is created");
  });

  $: {
    if (editor && content != editor.getHtml(true)) {
      editor.setHtml(content, true);
    }
  }
</script>

<!--Toast {isOpen} class="mr-1 align-text-bottom align-bottom" color="warning"-->
<!--Toast {isOpen} class="fixed-bottom" color="warning">
	<ToastHeader>Action status</ToastHeader>
	<ToastBody> {result.status} </ToastBody>
</Toast-->

<div class="h-100 pt-1" bind:this="{maindiv}" id="htmleditor-{uid}"></div>

<!--Toast {isOpen} class="fixed-bottom" color="warning">
	<ToastHeader>Action status</ToastHeader>
	<ToastBody> {result.status} </ToastBody>
</Toast-->
<style>
  :global(.cl) {
    height: 100%;
  }
  :global(.cl-content) {
    font-family: "uthmantn";
    font-size: 1rem !important;
  }

  /*
	:global(.icon) {
    display: inline-block;
    width: 0.5em;
    height: 0.5em;
    stroke-width: 0;
    stroke: currentColor;
    fill: currentColor;
    font-size: 32px;
  }*/

  /*
	:global(.blink) {       
    display: inline;
    color: inherit;
    animation: blink 1s steps(1) infinite;
    -webkit-animation: blink 1s steps(1) infinite;
	}
	@keyframes -global-blink { 
		50% { color: transparent; } 
	}
	@-webkit-keyframes -global-blink { 
		50% { color: transparent; } 
	}*/
</style>
