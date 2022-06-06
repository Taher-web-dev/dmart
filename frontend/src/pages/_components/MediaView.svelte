<script>
  //import { onMount } from "svelte";

  export let content_type;
  export let url;
  export let displayname = undefined;
  //export let description = undefined;

  //onMount(async () => {});

  /*
{#if description}
	{description}
{/if}*/
  //console.log("Rendering media entry", displayname, content_type, url);
</script>

{#if content_type.startsWith("image")}
  <img src="{url}" alt="{displayname}" class="mw-100" />
{:else if content_type.startsWith("audio")}
  <audio controls src="{url}">
    <track kind="captions" />
  </audio>
{:else if content_type.startsWith("video")}
  <video controls src="{url}">
    <track kind="captions" />
  </video>
{:else if content_type.startsWith("application/pdf")}
  <div class="h-100 w-100 vh-100 embed-responsive embed-responsive-16by9" style="overflow: hidden hidden;">
    <object title="{displayname}" class="h-100 w-100 embed-responsive-item" type="application/pdf" data="{url}">
      <p>For some reason PDF is not rendered here properly.</p>
    </object>
    <!--iframe src={url} title={displayname} class="embed-responsive-item" allowfullscreen ></iframe-->
  </div>
{:else}
  <a href="{url}" title="{displayname}">link {displayname}</a>
{/if}
