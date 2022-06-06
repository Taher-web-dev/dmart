<script>
  import Attachment from "./Attachment.svelte";
  import { _, number } from "../../i18n";
  import Icon from "./Icon.svelte";
  import ReplyModal from "./ReplyModal.svelte";
  import signedin_user from "../managed/_stores/signedin_user.js";
  import ContentModal from "../managed/_components/ContentModal.svelte";
  import { Button, ListGroup, ListGroupItem, CardBody, CardFooter } from "sveltestrap";
  import { dmart_entries } from "../../dmart.js";
  //import { entries } from "../managed/_stores/entries.js";
  export let data;
  export let extended;

  let media;
  let replies;

  $: {
    replies = data?.attachments?.reply || [];
    media = data?.attachments?.media || [];
  }

  let media_modal = false;
  let reply_modal = false;

  async function handle(event) {
    //console.log("Action: ", event);
    // TBD reload data
    const _entries = await dmart_entries(data.subpath, [], [data.shortname]);
    //if(_entries.length > 0) entries.add(data.subpath, {data: _entries[0]});
    //console.log("Action retrieved ... ", _entries);
    if (_entries.length > 0) data = _entries[0];
  }
</script>

{#if extended}
  <ContentModal
    subpath="{data.subpath}"
    parent_shortname="{data.shortname}"
    bind:open="{media_modal}"
    fix_resource_type="media"
    on:created="{handle}" />
  <ReplyModal
    subpath="{data.subpath}"
    parent_shortname="{data.shortname}"
    bind:open="{reply_modal}"
    on:created="{handle}" />

  <CardBody>
    <CardFooter class="py-2">
      {$_("attachments")} ({$number(media ? media.length : 0)})
      {#if $signedin_user}
        <div class="float-end mb-0 mt-n1">
          <Button href="#" title="Add" on:click="{() => (media_modal = true)}" size="sm" outline>
            <Icon name="plus-square-dotted" class="fs-6" />
          </Button>
        </div>
      {/if}
    </CardFooter>
    {#if media}
      <ListGroup>
        {#each media as attachment (attachment.uuid)}
          <ListGroupItem>
            <Attachment
              data="{attachment}"
              parent_shortname="{data.shortname}"
              on:updated="{handle}"
              on:deleted="{handle}" />
          </ListGroupItem>
        {/each}
      </ListGroup>
    {/if}
  </CardBody>

  <CardBody class="pt-2">
    <CardFooter class="py-2">
      {$_("replies")} ({$number(replies ? replies.length : 0)})

      <div class="float-end mb-0 mt-n1">
        <Button href="#" title="Add" on:click="{() => (reply_modal = true)}" size="sm" outline>
          <Icon name="plus-square-dotted" class="fs-6" />
        </Button>
      </div>
    </CardFooter>
    {#if replies}
      <ListGroup>
        {#each replies as attachment (attachment.uuid)}
          <ListGroupItem>
            <Attachment
              data="{attachment}"
              parent_shortname="{data.shortname}"
              on:updated="{handle}"
              on:deleted="{handle}" />
          </ListGroupItem>
        {/each}
      </ListGroup>
    {/if}
  </CardBody>
{/if}
