<script>
  import { Collapse, Navbar, NavbarToggler } from "sveltestrap";
  import { sections } from "../_stores/sections.js";
  import SidebarSection from "./SidebarSection.svelte";
  import SidebarItem from "./SidebarItem.svelte";

  let isOpen = false;

  function handleUpdate(event) {
    isOpen = event.detail.isOpen;
  }
</script>

<!-- TODO add search to the top -->
<Navbar color="light" light expand="md" class="px-1 me-2 mt-1 rounded-3">
  <NavbarToggler on:click="{() => (isOpen = !isOpen)}" />
  <Collapse isOpen="{isOpen}" navbar expand="md" on:update="{handleUpdate}">
    <ul class="w-100 px-1 ">
      {#each $sections as child}
        <li>
          {#if child.type === "section"}
            <SidebarSection path="{[]}" {...child} />
          {:else}
            <SidebarItem path="{[]}" {...child} />
          {/if}
        </li>
      {/each}
    </ul>
  </Collapse>
</Navbar>

<!-- TODO add search to the top -->
<style>
  ul {
    /*padding: 0.2em 0.2em 0 0; 0.2em 0.5em 0 0;*/
    /*margin: 0 0.5em 0 0;*/
    /*border-right: 1px solid #eee;*/
    list-style: none;
  }

  /*li {
    padding: 0.2em 0;
    }*/

  li:hover {
    z-index: 1;
    color: #495057;
    text-decoration: none;
    background-color: #f8f9fa;
  }
</style>
