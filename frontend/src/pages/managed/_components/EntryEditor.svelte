<script>
  import { active_entry, has_changed } from "../_stores/active_entry.js";
  import MarkdownEditor from "./MarkdownEditor.svelte";
  import HtmlEditor from "./HtmlEditor.svelte";
  import MediaView from "../../_components/MediaView.svelte";
  import History from "./History.svelte";
  import Attachments from "../../_components/Attachments.svelte";
  import { JSONEditor, createAjvValidator } from "svelte-jsoneditor";
  import { Nav, Button, ButtonGroup } from "sveltestrap";
  import Icon from "../../_components/Icon.svelte";
  import { _ } from "../../../i18n";
  import { website } from "../../../space_config";
  import { onDestroy } from "svelte";
  import { getNotificationsContext } from "svelte-notifications";
  import { dmart_update_embedded } from "../../../dmart";
  import { active_space } from "../_stores/active_space.js";
  import { get } from "svelte/store";
  import dmart_fetch from "../../../../custom-fetch.js";

  const { addNotification } = getNotificationsContext();

  let header_height;
  let content;
  let url;
  let schemaurl;
  let schema = {};
  let uid;
  let content_type;
  let resource_type;
  let shortname;
  let displayname;
  let subpath;
  let old_change_id;
  let new_change_id;
  let status;
  let data;
  let payload;
  let validator;

  const unsubscribe = active_entry.subscribe((value) => {
    if (!value.data) {
      uid = content = content_type = displayname = url = "";
      data = {};
      return;
    }

    data = value.data;
    uid = value.data.subpath + "/" + value.data.shortname;
    subpath = value.data.subpath;
    resource_type = value.data.resource_type;
    shortname = value.data.shortname;
    displayname = value.data.displayname;
    if (value.data.attributes.payload) {
      content = value.data.attributes.payload.embedded;
      content_type = value.data.attributes.payload.content_type;
      // FIXME: resource type (content) was hard coded here
      url = value.data.attributes.payload
        ? `${get(active_space).backend}/managed/payload/content/${
            website.space_name
          }/${data.subpath}/${value.data.attributes.payload}`
        : null;

      // FIXME: subpath (schema) was hard coded here
      // FIXME: manually added extention (.json) to end of schema short name
      schemaurl = value.data.attributes.payload
        ? `${get(active_space).backend}/managed/payload/schema/${
            website.space_name
          }/schema/${value.data.attributes.schema_shortname}.json`
        : null;
    } else {
      content = value.data;
      content_type = "unknown";
      url = "";
    }

    const headers = {
      Accept: "application/json",
      Connection: "close",
    };

    const request = {
      method: "GET",
      headers: headers,
      cache: "no-cache",
      mode: "cors",
    };

    dmart_fetch(url, request).then((resp) => (payload = { json: resp }));
    dmart_fetch(schemaurl, request).then((resp) => {
      schema = resp;
    });

    if (value.data.attributes && value.data.attributes.previous_change_id)
      old_change_id = value.data.attributes.previous_change_id;
    else old_change_id = "";
  });

  onDestroy(unsubscribe);

  function hasChanged() {
    let _has_changed =
      data &&
      data.attributes &&
      data.attributes.payload &&
      !(content === data.attributes.payload.embedded);
    if (_has_changed != $has_changed) {
      $has_changed = _has_changed;
    }
  }

  let tab_option = "edit";
  $: {
    status = "<b>" + ($has_changed ? "Modified" : "Uptodate") + "</b>";
    if (old_change_id) status += " " + old_change_id.substring(5, 13);
    if (new_change_id) status += " >> " + new_change_id.substring(5, 13);
  }

  function beforeUnload(event) {
    // Cancel the event as stated by the standard.
    if ($has_changed) {
      event.preventDefault();
      let message =
        "There are unsaved modifications. Are you sure you want to leave page?";
      event.returnValue = message; // Chrome requires returnValue to be set.
      return message; // more compatibility
    }
  }

  async function saveEntry() {
    if ($has_changed) {
      let result = await dmart_update_embedded(
        content_type,
        content,
        subpath,
        shortname,
        resource_type
      );
      if (result && result.attributes && result.attributes.previous_change_id)
        old_change_id = result.attributes.previous_change_id;
      else old_change_id = "";

      if (result && result.attributes && result.attributes.new_change_id)
        new_change_id = result.attributes.new_change_id;
      else new_change_id = "";

      $has_changed = false;
      active_entry.updatePayload(content, old_change_id);

      addNotification({
        text: `Update (${result.status}) ${old_change_id.substring(
          5,
          13
        )} >> ${new_change_id.substring(5, 13)}`,
        position: "bottom-center",
        type: result.status == "success" ? "success" : "warning",
        removeAfter: 5000,
      });
    }
  }

  async function togglePublishEntry() {}
  async function deleteEntry() {}

  $: validator = createAjvValidator(schema);
</script>

<svelte:window on:beforeunload={beforeUnload} />
<div bind:clientHeight={header_height}>
  <Nav class="w-100">
    <ButtonGroup size="sm" class="align-items-center">
      <!--span class="ps-2 pe-1"> {$_("shortname")} </span-->
      <span class="font-monospace"><small>{displayname}</small></span>
    </ButtonGroup>
    <ButtonGroup size="sm" class="ms-auto align-items-center">
      <span class="ps-2 pe-1"> {$_("views")} </span>
      <Button
        outline
        color="success"
        size="sm"
        class="justify-content-center text-center py-0 px-1"
        active={"edit" == tab_option}
        title={$_("edit")}
        on:click={() => (tab_option = "edit")}
      >
        <Icon name="pencil" />
      </Button>
      <Button
        outline
        color="success"
        size="sm"
        class="justify-content-center text-center py-0 px-1"
        active={"source" == tab_option}
        title={$_("source")}
        on:click={() => (tab_option = "source")}
      >
        <Icon name="code-slash" />
      </Button>
      <!--Button
        outline
        color="success"
        size="sm"
        class="justify-content-center text-center py-0 px-1"
        active="{'details' == tab_option}"
        title="{$_('details')}"
        on:click="{() => (tab_option = 'details')}"
      >
        <Icon name="info" />
      </Button-->
      <Button
        outline
        color="success"
        size="sm"
        class="justify-content-center text-center py-0 px-1"
        active={"attachments" == tab_option}
        title={$_("attachments")}
        on:click={() => (tab_option = "attachments")}
      >
        <Icon name="paperclip" />
      </Button>
      <Button
        outline
        color="success"
        size="sm"
        class="justify-content-center text-center py-0 px-1"
        active={"history" == tab_option}
        title={$_("history")}
        on:click={() => (tab_option = "history")}
      >
        <Icon name="clock-history" />
      </Button>
    </ButtonGroup>
    <!--ButtonGroup size="sm" class="align-items-center">
      <span class="ps-2 pe-1"> {$_("actions")} </span>
      <Button
        outline
        color="success"
        size="sm"
        title="{$_('activate')}"
        on:click="{togglePublishEntry}"
        class="justify-content-center text-center py-0 px-1"
      >
        <Icon name="file-check" />
      </Button>
      <Button
        outline
        color="success"
        size="sm"
        title="{$_('delete')}"
        on:click="{deleteEntry}"
        class="justify-content-center text-center py-0 px-1"
      >
        <Icon name="trash" />
      </Button>
    </ButtonGroup-->
    <ButtonGroup size="sm" class="align-items-center">
      <span class="ps-2 pe-1"> {$_("status")} </span>
      <Button
        outline
        color={$has_changed ? "danger" : "secondary"}
        title={$_("save")}
        size="sm"
        disabled={true}
        class="justify-content-center text-center py-0 px-1 me-1"
      >
        <span class="font-monospace text-{$has_changed ? 'danger' : 'success'}"
          ><small>{@html status}</small></span
        >
      </Button>
      <Button
        outline
        color={$has_changed ? "danger" : "secondary"}
        title={$_("save")}
        on:click={saveEntry}
        disabled={!$has_changed}
        size="sm"
        class="justify-content-center text-center py-0 px-1"
      >
        <Icon name="cloud-upload" />
      </Button>
    </ButtonGroup>
    <ButtonGroup>
      <Button
        outline
        color="success"
        size="sm"
        title={$_("close")}
        class="justify-contnet-center text-center py-0 px-1"
        on:click={() => {
          active_entry.reset();
        }}><Icon name="x-circle" /></Button
      >
    </ButtonGroup>
  </Nav>
</div>
<div
  class="px-1 pb-1 tab-content"
  style="height: calc(100% - {header_height}px); overflow: hidden auto;"
>
  <div class="h-100 tab-pane" class:active={tab_option === "source"}>
    <!--JSONEditor json={data} /-->
    <div
      class="px-1 pb-1 h-100"
      style="text-align: left; direction: ltr; overflow: hidden auto;"
    >
      <pre>
        {JSON.stringify(data, undefined, 1)}
      </pre>
    </div>
  </div>
  <div class="h-100 tab-pane" class:active={tab_option === "edit"}>
    {#if url && !data.attributes.payload.endsWith("json")}
      <MediaView {url} {displayname} {content_type} />
    {:else if content_type && content_type.startsWith("text/html;")}
      <HtmlEditor bind:content on:changed={hasChanged} />
    {:else if content_type && content_type.startsWith("text/markdown;")}
      <MarkdownEditor bind:content on:changed={hasChanged} />
    {:else if data.attributes.payload.endsWith("json")}
      {#if validator && payload}
        <JSONEditor
          {validator}
          bind:content={payload}
          on:changed={hasChanged}
        />
      {/if}
    {:else}
      <h4>Unrecognized conent type {content_type}</h4>
      <div
        class="px-1 pb-1 h-100"
        style="text-align: left; direction: ltr; overflow: hidden auto;"
      >
        <pre> {JSON.stringify(content, null, 1)} </pre>
      </div>
    {/if}
  </div>
  <div class="h-100 tab-pane" class:active={tab_option === "history"}>
    <History subpath={data.subpath} shortname={data.shortname} />
  </div>
  <div class="h-100 tab-pane" class:active={tab_option === "attachments"}>
    <Attachments {data} extended={true} />
  </div>
</div>

<style>
  span {
    color: dimgrey;
  }
</style>
