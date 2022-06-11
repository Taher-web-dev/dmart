<script>
  import { url, leftover, params, afterPageLoad, isChangingPage, ready } from "@roxi/routify";
  import { dmart_pub_query } from "../dmart.js";
  import EntryCard from "./_components/EntryCard.svelte";
  import { _, number } from "../i18n";
  import { Button, Row, Col } from "sveltestrap";
  import About from "./about.svelte";
  import Browse from "./_components/Browse.svelte";
  import { website } from "../space_config";

  export let scoped = {};
  scoped;
  export let scopedSync = {};
  scopedSync;

  let items = [];
  let available = 0;

  let viewType;
  let subpath;
  let shortnames;
  let parents = [];
  let search = "*";
  let queryType = "search";
  let resourceTypes = ["post", "biography", "reply", "share", "media", "reaction"];
  let pageTitle;
  let tags = [];

  function prep_page() {
    shortnames = [];
    search = "*";
    queryType = "search";

    //console.log("params: ", $params);
    //console.log("leftover: ", $leftover);
    // Trim "/" from beggning and end
    let lo = decodeURI($leftover);
    lo = lo.split("?")[0];
    if (lo.startsWith("/")) lo = lo.slice(1);
    if (lo.endsWith("/")) lo = lo.slice(0, -1);
    let path = lo.split("/");

    //console.log("Path: ", path);
    viewType = path[0]; // folder, tag, entry, search, random, recent
    if (!viewType) viewType = "folder";

    //console.log("viewType: ", viewType);
    subpath = path.slice(1, -1).join("/"); // All entries except first and last
    let shortname = path.slice(-1)[0]; // Last entry

    if (!subpath || !shortname) {
      shortname = "";
      subpath = path.length < 2 ? "posts" : path[1];
    }

    if (viewType == "search" && "q" in $params) {
      search = decodeURI($params.q);
      subpath += "/" + shortname;
      shortname = `"${search}"`;
    }

    //console.log("Subpath: ", subpath);
    pageTitle = shortname;

    //metatags.title = pageTitle;
    //metatags.description = 'Routes for Svelte'

    //console.log("Viewtype: ", viewType, " Shortname: ", shortname);
    switch (viewType) {
      case "entry":
        queryType = "subpath";
        shortnames.push(shortname);
        break;
      case "tag":
        //queryType = "tags";
        if (shortname && shortname.trim() != "") {
          search = `@tags:{${shortname}}`;
          //console.log("Search: ", search);
        }
        break;
      case "folder":
        if (shortname) subpath = `${subpath}/${shortname}`;
        break;
      case "random":
        queryType = "random";
        break;
      case "search":
        queryType = "search";
        if (shortname)
          //subpath = "/posts";
          break;
      case "recent":
        queryType = "recent";
        break;
      default:
    }

    //console.log("queryType: ", queryType);
    parents = subpath.split("/");
    //if( (viewType == "entry") && shortname)
    //	parents.push(shortname);

    parents = parents;
    if (viewType == "entry") parents.push(" ");
  }

  $afterPageLoad(() => {
    let oldsubpath = subpath;
    let oldshortnames = shortnames.join();
    let oldpagetitle = pageTitle;

    prep_page();
    //console.log("old subpath: ", oldsubpath, "old shortnames: ", oldshortnames);
    //console.log("subpath: ", subpath, "shortnames: ", shortnames);
    if (oldsubpath != subpath || oldshortnames != shortnames.join() || oldpagetitle != pageTitle) {
      items = [];
      load_tags();
      load_next();
    }
  });

  async function load_tags() {
    let resp = await dmart_pub_query(subpath, resourceTypes, [], viewType == "tag" ? "tags" : "folders");
    if(resp.records.size > 0) tags = resp.records[0].attributes.tags;
    //console.log("Tags: ", tags, "parents: ", parents.join("/"), "qt: ", queryType);
  }

  async function load_next() {
    let resp = await dmart_pub_query(subpath, resourceTypes, shortnames, queryType, search, 10, items.length);
    // console.log("Resp result: ", resp.results);
    if (resp && resp.records) {
      items = [...items, ...resp.records];
      available = resp.results[0].attributes.total;
    }
    //if(viewType == "entry" && items.length > 0)
    //	pageTitle = items[0].attributes.displayname;

    items = items;
    //console.log("Subpath: ", subpath, "shortnames: ", shortnames, "querytype: ", queryType, "search: ", search, "Entries retrieved: ", items.length, " Total available: ", available);
    //debugger
  }

  async function load_more(event) {
    event.preventDefault();
    if (available > items.length) {
      await load_next();
    }
  }

  prep_page();
  load_tags()
    .then(() => {
      load_next()
        .then(() => {
          $ready();
        })
        .catch(console.log);
    })
    .catch(console.log);
</script>

<svelte:head>
  <meta name="Description" content="{website.description}" />
  <title>{pageTitle}</title>
</svelte:head>

<!-- routify:options param-is-page=true -->
{#if !$isChangingPage}
  <Row>
    <Col>
      {#if location.pathname == "/"}
        <About />
      {/if}
      {#each parents as parent, i}
        {#if parent}
          {#if i == 0}
            <b>
              ::<Button color="link" outline href="{$url(`/${viewType == 'tag' ? 'tag' : 'folder'}/${parent}`)}">
                {$_(parent)}
              </Button>
            </b>
          {:else if i == parents.length - 1}
            <b> ::<Button disabled color="link" outline>{parent}</Button> </b>
          {:else}
            <b>
              ::<Button
                color="link"
                outline
                href="{$url(`/${viewType == 'tag' ? 'tag' : 'folder'}/${parents.slice(0, i + 1).join('/')}`)}">
                {parent}
              </Button>
            </b>
          {/if}
        {/if}
      {/each}
      {#if viewType == "search" || viewType == "tag" || viewType == "entry"}
        <b> ::<Button disabled color="link" outline>{pageTitle}</Button> </b>
      {/if}
      ( {$number(items.length)} / {$number(available)} )
      <br />
      <Browse parents="{parents}" tags="{tags}" viewType="{viewType}" />
      <hr />
    </Col>
  </Row>
  <Row>
    <Col>
      {#each items as item}
        <EntryCard data="{item}" extended="{items.length == 1}" />
      {/each}
      {#if available > items.length}
        <Button on:click="{load_more}" title="More" size="md" color="success" class="float-end">
          {$_("x_items_left_click_for_more", {
            values: { count: $number(available - items.length) },
          })}
        </Button>
      {:else if items.length > 1}
        <Button on:click="{load_more}" title="More" size="md" color="success" disabled class="float-end" outline>
          {$_("all_x_items_are_loaded", {
            values: { count: $number(items.length) },
          })}
        </Button>
      {/if}
    </Col>
  </Row>
{/if}
