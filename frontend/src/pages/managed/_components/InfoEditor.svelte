<script>
  import Input from "../../_components/Input.svelte";
  import Form from "../../_components/Form.svelte";
  import { _ } from "../../../i18n";
  import { dmart_content, dmart_postmedia } from "../../../dmart";
  import sha1 from "../../../sha1";
  export let subpath = null;
  export let data = null;
  export let parent_shortname = undefined;
  export let fix_resource_type = undefined;
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();

  let shortname;
  let displayname;
  let resource_type;
  let payload = "";
  let payload_type = "text/html";
  let tags;
  let description;

  resource_type = fix_resource_type ? fix_resource_type : "post";

  $: {
    if (data) {
      subpath = data.subpath;
      shortname = data.shortname;
      displayname = data.displayname;
      description = data.attributes.description;
      resource_type = data.resource_type;
      if ("attributes" in data && "embedded" in data.attributes && data.attributes.payload.embedded)
        payload = data.attributes.payload.embedded;
      if ("attributes" in data && "tags" in data.attributes);
      tags = data.attributes.tags.join(",");
    } else {
    }
  }

  async function create() {
    let record = {
      resource_type: resource_type,
      subpath: subpath,
      shortname: shortname,
      attributes: {
        displayname: displayname,
        description: description,
        tags: tags.split(","),
      },
    };

    if (parent_shortname) record.parent_shortname = parent_shortname;

    if (enableUpload) {
      console.log("My sha1: ", mediafile.sha1);
      record.attributes.payload = {
        checksum: `sha1:${mediafile.sha1}`,
        filepath: mediafile.name,
        content_type: mediafile.type,
        bytesize: mediafile.size,
      };
      //record.attributes.filename = mediafile.name;
    } else if (data == null) {
      // Only create payload for new entries
      record.attributes.payload = {
        checksum: `sha1:${sha1(payload)}`,
        embedded: payload,
        content_type: `${payload_type}; charset=utf8`,
        bytesize: new Blob([payload]).size,
      };
    }
    console.info("Record: ", record);
    let resp;
    if (resource_type != "media")
      if (data) {
        // Fix subpath if the type is folder.
        if (resource_type == "folder" && subpath.endsWith(shortname)) {
          record.subpath = subpath.substring(0, subpath.lastIndexOf("/"));
          console.log(`Fixing subpath: from ${subpath} to ${record.subpath}`);
        }
        resp = await dmart_content("update", record);
        dispatch("updated", record);
      } else {
        resp = await dmart_content("create", record);
        dispatch("created", record);
      }
    else resp = await dmart_postmedia(record, mediafile);

    console.log("Resp: ", resp.results[0]);
  }

  let enableUpload = "media" == resource_type;
  function resourceTypeChanged(event) {
    console.log(event.target.value);
    enableUpload = "media" == event.target.value;
  }

  let mediafile;
  function uploadMedia(event) {
    mediafile = event.target.files[0];
    console.log("Name: ", mediafile.name, "Size: ", mediafile.size);
    var reader = new FileReader();
    reader.onload = function (event) {
      mediafile["sha1"] = sha1(event.target.result);
      console.log("Completed reading file: ", mediafile.sha1);
    };
    reader.readAsArrayBuffer(mediafile);
  }
</script>

<h4>
  {#if data}{$_("edit_entry")}{:else}{$_("create_entry")}{/if}
</h4>

<Form>
  <Input id="subpath" title="{$_('subpath')}" value="{subpath}" readonly="{true}" type="text" />
  <Input id="shortname" title="{$_('shortname')}" bind:value="{shortname}" type="text" />
  <Input id="displayname" title="{$_('displayname')}" bind:value="{displayname}" type="text" />
  <Input id="tags" title="{$_('tags')}" bind:value="{tags}" type="text" />
  <Input id="description" type="textarea" title="{$_('description')}" bind:value="{description}" />

  {#if fix_resource_type || data}
    <Input id="resource_type" title="{$_('resource_type')}" value="{resource_type}" readonly="{true}" type="text" />
  {:else}
    <Input
      id="resource_type"
      type="select"
      title="{$_('resource_type')}"
      bind:value="{resource_type}"
      on:change="{resourceTypeChanged}">
      <option value="folder">{$_("folder")}</option>
      <option value="post">{$_("post")}</option>
      <option value="contact">{$_("contact")}</option>
      <option value="media">{$_("media")}</option>
      <option value="biography">{$_("biography")}</option>
      <option value="term">{$_("term")}</option>
    </Input>
  {/if}

  {#if !data && resource_type != "folder"}
    {#if enableUpload}
      <Input id="upload" title="{$_('upload')}" type="file" on:change="{uploadMedia}" />
    {:else}
      <Input id="payload" type="textarea" title="{$_('payload')}" bind:value="{payload}" />
      <Input id="payload_type" title="{$_('payload_type')}" bind:value="{payload_type}" type="select">
        <option value="text/html">{$_("text_html")}</option>
        <option value="text/markdown">{$_("text_markdown")}</option>
        <option value="text/json">{$_("text_json")}</option>
      </Input>
    {/if}
  {/if}
</Form>
<!--ModalFooter>
		<Button color="secondary" on:click={cancel}>{$_("cancel")}</Button>
		<Button color="primary" on:click={create}>{$_("accept")}</Button>
  </ModalFooter-->
