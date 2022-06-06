<script>
  import { Badge, Button } from "sveltestrap";
  import { url } from "@roxi/routify";
  import { number } from "../../i18n";

  export let name;
  export let frequency = false;
</script>

<Button alt="{name}" class="m-1" href="{$url(`/tag/posts/${name}`)}" color="primary" outline size="sm">
  {name}
  {#if frequency}
    <Badge color="secondary">{$number(frequency)}</Badge>
  {/if}
</Button>
