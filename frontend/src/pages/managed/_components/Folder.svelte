<script>
  import { dmart_entries, dmart_folder } from "../../../dmart.js";
  import { entries } from "../_stores/entries.js";
  import Icon from "../../_components/Icon.svelte";
  import File from "./File.svelte";
  import { getNotificationsContext } from "svelte-notifications";
  import ContentModal from "./ContentModal.svelte";
  import { _ } from "../../../i18n";

  const { addNotification } = getNotificationsContext();

  let expanded = false;
  //let children_loaded = false;
  export let data;

  let children_subpath;
  let displayname;

  $: {
    children_subpath = data.subpath + "/" + data.shortname;
    displayname = data.displayname.length < 20 ? data.displayname : data.displayname.substring(0, 20) + " ...";
  }
  async function toggle() {
    expanded = !expanded;
    if (!$entries[children_subpath]) {
      const _entries = await dmart_entries(children_subpath, []);
      $entries[children_subpath] = [];
      _entries.forEach((_entry) => {
        $entries[children_subpath].push({ data: _entry });
      });
    }
  }

  let entry_create_modal;
  async function handleEntryCreated(event) {
    //let _name = prompt("Enter the new folder shortname", "");
    /*let entry = { data: event.detail };
    entry.data.displayname = entry.data.attributes.displayname;
    entry.data.subpath = children_subpath;
    entries.add(children_subpath, entry);
  console.log("Created entry", entry);*/
    /* 
    let result = await dmart_folder("create", children_subpath, entry.data.shortname);
    addNotification({
      text: `Created new folder "${entry.data.shortname}" under ${children_subpath}`,
      position: "bottom-center",
      type: result.status == "success" ? "success" : "warning",
      removeAfter: 5000,
    });
    if (result.status == "success") {
      entries.add(children_subpath, entry);
  }*/
  }

  let folder_details_modal;
  //function folderDetailsModal() {
  //}

  async function deleteFolder() {
    if (
      confirm(
        `Are you sure you want to delete the folder "${data.shortname}|${data.displayname}" under ${data.subpath}?`
      )
    ) {
      let result = await dmart_folder("delete", data.subpath, data.shortname);
      addNotification({
        text: `Deleted folder "${data.shortname}|${data.displayname}" under ${data.subpath}`,
        position: "bottom-center",
        type: result.status == "success" ? "success" : "warning",
        removeAfter: 5000,
      });
      if (result.status == "success") {
        entries.del(data.subpath, data.shortname);
      }
    }
  }
</script>

<ContentModal subpath="{children_subpath}" bind:open="{entry_create_modal}" on:created="{handleEntryCreated}" />
<ContentModal bind:open="{folder_details_modal}" fix_resource_type="folder" data="{data}" />

<span class:expanded class="folder position-relative mt-1 ps-2" on:click="{toggle}">
  <span style="overflow: hidden;">
    <Icon class="text-start" name="folder{expanded ? '2-open' : ''}" />
    {displayname}
  </span>
  <span class="toolbar top-0 end-0 position-absolute px-0">
    <span class="px-0" title="{$_('create_subentry')}" on:click|stopPropagation="{() => (entry_create_modal = true)}">
      <Icon name="file-plus" />
    </span>
    <span class="px-0" title="{$_('edit')}" on:click|stopPropagation="{() => (folder_details_modal = true)}">
      <Icon name="pencil" />
    </span>
    <span class="px-0" title="{$_('delete')}" on:click|stopPropagation="{deleteFolder}">
      <Icon name="trash" />
    </span>
  </span>
</span>

{#if expanded && $entries[children_subpath]}
  <ul class="py-1 ps-1 ms-2 border-start">
    {#each $entries[children_subpath] as child (children_subpath + child.data.shortname)}
      <li>
        {#if child.data.resource_type === "folder"}
          <svelte:self data="{child.data}" />
        {:else}
          <File data="{child.data}" />
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .folder {
    /*font-weight: bold;*/
    cursor: pointer;
    display: list-item;
    list-style: none;
    border-top: thin dotted grey;
  }

  .folder:hover {
    z-index: 2;
    color: #495057;
    text-decoration: none;
    background-color: #e8e9ea;
  }

  .expanded {
    background-color: #e8e9ea;
    border-bottom: thin dotted green;
  }

  ul {
    list-style: none;
  }

  li {
    padding: 0;
  }

  .toolbar {
    display: none;
    color: brown;
  }

  .toolbar span:hover {
    color: green;
  }

  .folder:hover .toolbar {
    display: flex;
  }
</style>
