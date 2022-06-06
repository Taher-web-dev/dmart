<script>
  import Form from "../../_components/Form.svelte";
  import Input from "../../_components/Input.svelte";
  import { _ } from "../../../i18n";
  import { dmart_query } from "../../../dmart.js";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  async function handleResponse(event) {
    let query = event.detail;
    query.resource_types = [query.resource_types, "reply", "share", "reaction"];
    if (query.resource_types != "media") query.resource_types.push("media");
    query.resource_shortnames = query.resource_shortnames.split(",");
    query.limit = parseInt(query.limit, 10);
    query.offset = parseInt(query.offset, 10);
    let json = await dmart_query(query);
    console.log("Query: ", query);
    console.log("Resposne: ", json);
    dispatch("response", json);
  }
</script>

<Form title="_________" on:response="{handleResponse}">
  <Input id="query_type" type="select" title="{$_('query_type')}">
    <option value="search">{$_("search")}</option>
    <option value="subpath">{$_("subpath")}</option>
    <option value="random">{$_("random")}</option>
    <option value="tags">{$_("tags")}</option>
    <option value="folders">{$_("folders")}</option>
    <option value="logs">{$_("logs")}</option>
    <option value="history">{$_("history")}</option>
  </Input>
  <Input id="subpath" type="text" title="{$_('subpath')}" value="/posts" />
  <Input id="search" type="text" title="{$_('search')}" value="*" />
  <Input id="resource_types" type="select" title="{$_('resource_types')}">
    <option value="post">{$_("post")}</option>
    <option value="folder">{$_("folder")}</option>
    <option value="biography">{$_("biography")}</option>
    <option value="contact">{$_("contact")}</option>
    <option value="media">{$_("media")}</option>
  </Input>
  <Input id="resource_shortnames" type="text" title="{$_('shortnames')}" />
  <Input id="limit" type="number" title="{$_('limit')}" value="{10}" />
  <Input id="offset" type="number" title="{$_('offset')}" value="{0}" />
</Form>
