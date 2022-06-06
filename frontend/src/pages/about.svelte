<script>
  import { website } from "../space_config";
  import LocalizedValue from "./_components/LocalizedValue.svelte";
</script>

<div class="bg-light bg-gradient px-4 py-2 rounded-3 my-1 text-white-25 border border-success ">
  <LocalizedValue field="{website.about}" />
</div>
