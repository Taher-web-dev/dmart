<script>
  import { afterPageLoad, params, url } from "@roxi/routify";
  import { _, date, number } from "../../i18n";
  import { Button, Badge } from "sveltestrap";

  export let parents = ["posts"];
  export let viewType = "folder";
  export let tags = [];

  let url_path;
  let url_params;

  function load_page() {
    url_params = "";
    url_path = `/${viewType}/${parents.join("/")}/`.replace("//", "/");
    if (viewType == "search") {
      if ("q" in $params) {
        url_params = "?q=" + decodeURI($params.q);
      }
    }
  }

  load_page();

  $afterPageLoad((event) => {
    load_page();
  });
</script>

<!-- routify:options param-is-page=true -->

{#if tags.length > 1}
  {#each tags as item}
    <Button
      alt="{item.tag}"
      class="m-1"
      href="{$url(url_path + item.tag + url_params)}"
      color="primary"
      outline
      size="sm">
      {item.tag}
      {#if item.frequency}
        <Badge color="secondary">{$number(item.frequency)}</Badge>
      {/if}
    </Button>
  {/each}
{/if}
