<script>
  import { dmart_entries } from "../../../dmart.js";
  import { active_section } from "../_stores/active_section.js";
  import { active_entry } from "../_stores/active_entry.js";
  import Folder from "./Folder.svelte";
  import File from "./File.svelte";
  import Icon from "../../_components/Icon.svelte";
  import { _ } from "../../../i18n";
  //import { onDestroy } from "svelte";
  import { url, isActive } from "@roxi/routify";
  import { entries } from "../_stores/entries.js";
  import { status_line } from "../_stores/status_line.js";
  import { ListGroup, ListGroupItem } from "sveltestrap";

  // Section components
  // import QueryForm from "./QueryForm.svelte";

  const components = {
    // "queryform": QueryForm
  };

  let query_type = "subpath";
  let resource_types = []; // ["folder", "post", "media"];
  let shortnames = [];
  let search = "";
  let max_returned_items = 100;
  //let entries = {};
  //let subpaths = [];

  //let children = [];
  //let name = "";
  //let icon = "";

  //const unsubscribe = active_section.subscribe((value) => {
  $: {
    //name = $active_section.name;
    //icon = $active_section.icon;
    resource_types = $active_section.resource_types;
    //children = $active_section.children;
    for (let child of $active_section.children) {
      if (
        child.type &&
        child.type == "folder" &&
        child.dmart_path &&
        !(child.dmart_path in $entries)
      ) {
        let subpath = child.dmart_path;
        dmart_entries(
          subpath,
          resource_types,
          shortnames,
          query_type,
          search,
          max_returned_items
        ).then((_entries) => {
          $entries[subpath] = []; // Empty the list of entries for the subpath
          _entries.forEach((_entry) => {
            $entries[subpath].push({ data: _entry });
          });
        });
      }
    }
  }
  //});

  //onDestroy(unsubscribe);

  let head_height;
  let foot_height;

</script>

<div bind:clientHeight={head_height}>
  <h5 class="my-0">
    {#if $active_section.icon}<Icon
        name={$active_section.icon}
        class="pe-1"
      />{/if}
    {#if $active_section.name}{$_($active_section.name)}{/if}
  </h5>
  <hr class="w-100 mt-1 mb-0" />
</div>
<div
  class="no-bullets scroller pe-0 w-100"
  style="height: calc(100% - {head_height +
    foot_height}px); overflow: hidden auto;"
>
  <ListGroup flush class="w-100">
    {#each $active_section.children as child ($active_section.name + child.name)}
      {#if child.type == "link"}
        <!--p class="my-0 font-monospace"><small>{JSON.stringify(child, undefined,1)}</small></p-->
        <ListGroupItem
          color="light"
          action
          href={$url("/managed/" + $active_section.name + "/" + child.name)}
          active={$isActive(
            "/managed/" + $active_section.name + "/" + child.name
          )}
        >
          {#if child.icon}<Icon name={child.icon} class="pe-1" />{/if}
          {$_(child.name)}
        </ListGroupItem>
      {:else if child.type == "component" && child.name in components}
        <svelte:component this={components[child.name]} />
      {:else if child.type == "folder" && $entries[child.dmart_path] && $entries[child.dmart_path].length > 0}
        <ListGroupItem class="px-0">
          <!--b> {child.name}</b> <br/-->
          <div class="mb-2">
            <Icon name="diagram-3" class="me-1" />
            {$_("entries_of")} <b>{$_(child.dmart_path)}</b>
          </div>

          {#each $entries[child.dmart_path] as entry (child.dmart_path + entry.data.shortname)}
            <Folder data={entry.data} />
          {/each}
        </ListGroupItem>
      {/if}
    {/each}
  </ListGroup>
</div>
<div class="w-100" bind:clientHeight={foot_height}>
  {#if $active_entry.data}
    <hr class="my-0" />
    <p class="lh-1 my-0">
      <small>
        <span class="text-muted">{$_("path")}:</span>
        {$active_entry.data.subpath}/{$active_entry.data.shortname} <br />
        <span class="text-muted">{$_("displayname")}:</span>
        {$active_entry.data.displayname} <br />
        <span class="text-muted">{$_("content_type")}:</span>
        {$active_entry?.data?.attributes?.payload?.content_type?.split(
          ";"
        )[0] || "uknown"}
      </small>
    </p>
  {/if}
  {#if $status_line}
    <hr class="my-1" />
    {@html $status_line}
  {/if}
</div>
