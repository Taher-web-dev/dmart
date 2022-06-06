<script>
  import EntryEditor from "./_components/EntryEditor.svelte";
  import { active_entry } from "./_stores/active_entry.js";
  import { _ } from "../../i18n";

  export let scoped;
  scoped;
  export let scopedSync;
  scopedSync;
</script>

{#if $active_entry.data}
  <EntryEditor />
{:else}
  <div class="alert alert-warning alert-dismissible fade show text-center m-2" role="alert">
    {@html $_("select_entry_from_sidebar")}
  </div>
{/if}
