<script>
  import SidebarItem from "./SidebarItem.svelte";
  import Icon from "./Icon.svelte";
  import { _ } from "../../i18n";

  export let path;
  export let expanded;
  export let id;
  export let children;
  export let type;
  export let icon;
  $: displayname = $_(id);

  path.push(id);
  async function toggle() {
    expanded = !expanded;
    //console.log("Expanding: ", path, expanded);
  }

  type = type; // silence the warning
</script>

<div class="mb-3">
  <span class:expanded on:click="{toggle}" class="py-1 ps-1">
    <Icon name="{icon}" class="me-1" />
    <b>{displayname}</b>
  </span>
  {#if expanded}
    <ul class="border-start pt-1 px-1 ms-1 ">
      {#each children as child}
        <li class="px-1 py-1">
          {#if child.type === "section"}
            <svelte:self path="{path}" {...child} />
          {:else}
            <SidebarItem path="{path}" {...child} />
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  span {
    /*padding: 0 0 0 0.5em;*/
    cursor: pointer;
    display: list-item;
    border-top: thin solid green;
  }

  .expanded {
    background-color: #e8e9ea;
  }

  ul {
    /*padding: 0.2em 0 0 0.5em;
    margin: 0 0 0 0.5em;*/
    list-style: none;
    /*border-left: 1px solid #eee;*/
  }

  li:hover {
    z-index: 2;
    color: #495057;
    text-decoration: none;
    background-color: #e8e9ea;
  }

  /*li {
    padding: 0.2em 0;
    margin-top: 0.2em;
    }*/
</style>
