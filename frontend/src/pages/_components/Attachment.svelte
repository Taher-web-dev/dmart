<script>
  import Icon from "./Icon.svelte";
  import MediaView from "./MediaView.svelte";
  import { Button } from "sveltestrap";
  import { date } from "../../i18n";
  import { dmart_delete_content } from "../../dmart";
  import signedin_user from "../managed/_stores/signedin_user.js";
  import ContentModal from "../managed/_components/ContentModal.svelte";
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();

  export let data;
  export let parent_shortname;
  // console.log("Attachment details: ", data);
  let author = "";
  if ("author" in data.attributes) author = data.attributes.author.shortname;

  let datetime = "";
  if ("created_at" in data.attributes && data.attributes.created_at) {
    //console.log( "x[", data.shortname, "]x >> y[", data.attributes.created_at, "]y");
    datetime = $date(Date.parse(data.attributes.created_at.replace(" ", "T").replace(" UTC", "").replace(" ", "")), {
      format: "short",
    });
  }

  async function deleteAttachment() {
    if (confirm(`Are you sure you want to delete the attachment "${data.displayname}|${data.shortname}"?`)) {
      console.log("User requested to delete: ", data.shortname, " childof: ", data.subpath);
      let resp = await dmart_delete_content(data.resource_type, data.subpath, data.shortname, parent_shortname);
      console.log("Result: ", resp);
      dispatch("deleted", { shortname: data.shortname, subpath: data.subpath });
    }
  }

  let details_modal = false;
</script>

{#if $signedin_user}
  <ContentModal bind:open="{details_modal}" fix_resource_type="{data.resource_type}" data="{data}" on:updated />
  <div class="float-end mb-0">
    <Button
      href="/managed/{data.subpath}/{data.shortname}"
      title="Manage"
      size="sm"
      outline
      on:click="{() => (details_modal = true)}">
      <Icon name="pencil" />
    </Button>
    <Button href="#" title="Delete" on:click="{deleteAttachment}" size="sm" outline>
      <Icon name="trash" />
    </Button>
  </div>
{/if}
<Icon name="person" />
{author}
<Icon name="clock" />
{datetime} <br />
{#if data.resource_type == "reply"}
  {#if data.attributes.displayname}
    {data.attributes.displayname} -
  {/if}
  {data.attributes.payload.embedded}
{:else if data.resource_type == "media"}
  <MediaView content_type="{data.attributes.payload.content_type}" url="{data.url}" displayname="{data.displayname}" />
{/if}
