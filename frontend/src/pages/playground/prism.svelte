<script>
  import { metatags } from "@roxi/routify";
  metatags.title = "Routify Prismjs Example";
  import { onMount } from "svelte";
  let Prism;
  let code = "let b = 4;";
  //alert("here");
  onMount(async () => {
    //alert("here here");
    const prismModule = await import("svelte-prismjs");
    await import("prismjs/components/prism-c.js");
    await import("prismjs/components/prism-json.js");
    //await import("prism-svelte");
    //await import("prismjs/plugins/line-highlight/prism-line-highlight.js");
    //await import("prismjs/plugins/file-highlight/prism-file-highlight.js");
    //alert("here here");
    // Once everything is loaded load the prismjs module
    Prism = prismModule.default;
    /*setInterval(() => {
      code = code == "let b = 4;" ? "let c = 323;" : "let b = 4;";
      console.log("should notice change");
  }, 3000);*/ // I don't need this, kefah.
  });
</script>

<h1>Examples</h1>

<p>This shows some simple examples of how to use sveltejs-prism plugin.</p>

<svelte:component this="{Prism}">
  {JSON.stringify({ hello: "World" }, undefined, 1)}
</svelte:component>

<h2>Javascript Language Simple</h2>

<svelte:component this="{Prism}">
  {`let b = 3;
function helloworld() {
	console.log("Hello World");
}
`}
</svelte:component>

<h2>Javascript With Line Numbers</h2>

<svelte:component this="{Prism}" showLineNumbers="{true}">
  {`
	let b = 3;
function helloworld() {
	console.log("Hello World");
}
`}
</svelte:component>

<h2>C language with line numbers no white space cleanup</h2>

<svelte:component
  this="{Prism}"
  language="c"
  normalizeWhiteSpace="{false}"
  code="{`
	
	int b =3;
int c = 32;
`}" />

<h2>C language with line numbers with white space cleanup</h2>

<svelte:component
  this="{Prism}"
  showLineNumbers="{true}"
  language="c"
  code="{`
	
	int b =3;
int c = 32;
`}" />

<h2>Example showing code can change every 3 seconds</h2>
<svelte:component this="{Prism}" showLineNumbers="{true}" code="{code}" />

<h2>Example using prism plugin not supported out of the box.</h2>

<p>
  We are using the
  <a href="https://prismjs.com/plugins/line-highlight/"> line highlight plugin </a>
  plugin which requires the data-line attribute to be passed in. Other plugins just require you to include the js after the
  component is imported
</p>
<svelte:component this="{Prism}" data-line="3,5-8">
  {`
onMount(() => {
	if (normalizeWhiteSpace) {
		Prism.plugins.NormalizeWhitespace.setDefaults(normalizeWhiteSpaceConfig);
	}
});
afterUpdate(async () => {
	// code variable if they are using a prop
	if (fakeCodeEl && fakeCodeEl.innerHTML !== "") {
		code = fakeCodeEl.innerHTML.trim();
	}
	// We need to wait till everything been rendered before we can
	// call highlightAll and load all the plugins
	await tick();
	// This will make sure all the plugins are loaded
	// Prism.highlight will not do that
	Prism.highlightAll();
});
`}
</svelte:component>

<style global>
  /*@import "highlight.js/styles/a11y-light.css";*/
  @import "prismjs/plugins/line-numbers/prism-line-numbers.css";
  @import "prismjs/plugins/command-line/prism-command-line.css";
  @import "prismjs/plugins/line-highlight/prism-line-highlight.css";
  @import "prismjs/themes/prism.css";
  @import "prismjs/themes/prism-coy.css";
</style>
