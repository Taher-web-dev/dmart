<script>
  import { redirect } from "@roxi/routify";
  import { _ } from "../../i18n";
  import { active_subsection } from "../_stores/active_subsection.js";
  import Icon from "./Icon.svelte";

  export let path;
  export let id;
  export let type;
  export let icon;
  export let description = undefined;
  export let link;

  $: displayname = $_(id);
  async function show_item() {
    //console.log("Requested to show item: ", path.join("|"), id, displayname);
    $active_subsection = { path: path, id: id, displayname: displayname };
    if (!link.startsWith("http") && !link.startsWith("/")) {
      link = "/" + link;
    }

    if (link.startsWith("http")) window.location.href = link;
    else $redirect(link);

    //window.location.href = `/${link}`;
  }
  type = type; // Silence the warning
</script>

<span on:click="{show_item}" class=" " title="{description}">
  <Icon name="{icon}" class="" />
  {displayname}
</span>

<style>
  span {
    cursor: pointer;
    display: list-item;
  }
</style>
