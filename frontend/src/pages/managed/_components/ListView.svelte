<script>
  import VirtualList from "svelte-tiny-virtual-list";
  import InfiniteLoading from "svelte-infinite-loading";
  import { dmart_query } from "../../../dmart";
  import { _, number } from "../../../i18n";
  import { onDestroy } from "svelte";
  import { status_line } from "../_stores/status_line.js";

  onDestroy(() => status_line.set(""));
  export let query;
  export let cols;
  export let details_split = 0;

  let total;
  let lastbatch;
  let page = 0;
  let items = [{}];
  let current_item = {};
  let api_status = "-";

  async function infiniteHandler({ detail: { loaded, complete, error } }) {
    try {
      query.limit = 50;
      query.offset = 50 * page;
      dmart_query(query)
        .then((json) => {
          const records = json.records
            .map((one) => {
              delete one.attributes["results-attributes"].backtrace;
              delete one.attributes["results-attributes"].auth_token;
              return one;
            })
            .reverse();
          if (json?.results[0].status == "success") {
            lastbatch = json.results[0].attributes.returned;
            total = json.results[0].attributes.total;
            // console.log(lastbatch, records);
            if (lastbatch) {
              page += 1;
              items = [...items, ...records];
              loaded();
              // complete();
              // console.log("New: ", lastbatch, "Loaded: ", items.length, "Page: ", page, "Total: ", total);
            } else {
              complete();
            }
            api_status = "success";
            status_line.set(`Loaded ${items.length - 1} of ${total}.<br/>api: ${api_status}`);
          } else {
            console.log("Error with query", json);
            api_status = json?.results[0] || "Unknown error";
            status_line.set(`api: ${api_status}`);
          }
        })
        .catch((e) => {
          console.log(e);
          error();
        });
    } catch (e) {
      console.log(e);
      error();
    }
  }

  function value(path, data, type) {
    //console.log("path: ", path, "data: ", data, "type: ", type);
    if (path.length == 1 && path[0].length > 0 && path[0] in data) {
      if (type == "number") return $number(data[path[0]]);
      else if (type == "json") return JSON.stringify(data[path[0]], undefined, 1);
      //else if (type == "timestamp") return $date(new Date(data[path[0]]), { format: "long" });
      //else if (type == "timestamp") return $_('datetime', { values: { ts: new Date(data[path[0]]) } });
      else return data[path[0]];
    }

    if (path.length > 1 && path[0].length > 0 && path[0] in data) {
      return value(path.slice(1), data[path[0]], type);
    }

    return $_("not_applicable");
  }
  let listHeight;
  let resizing = false;
  function resize(e) {
    if (resizing) {
      details_split = details_split - e.movementY > 0 ? details_split - e.movementY : 0;
    }
  }
  //$: console.log (details_split, resizing);
</script>

<svelte:window on:mouseup="{() => (resizing = false)}" on:mousemove="{resize}" />
<div class="list h-100" bind:offsetHeight="{listHeight}">
  <VirtualList
    height="{listHeight - details_split - 5}"
    width="auto"
    stickyIndices="{[0]}"
    itemCount="{items.length}"
    overscanCount="{100}"
    itemSize="{25}">
    <!--div slot="header" style="padding: 0 15px;"> 
    </div-->
    <div
      slot="item"
      let:index
      let:style
      style="{style.replaceAll('left:0;', '')}"
      class="my-row"
      on:click="{() => {
        current_item = index;
      }}"
      class:current="{current_item == index}">
      {#if index == 0}
        <div class="my-cell" style="width: 5%;">#</div>
        {#each Object.keys(cols) as col}
          <div class="my-cell" style="width: {cols[col].width};"><strong>{cols[col].title}</strong></div>
        {/each}
      {:else}
        <div class="my-cell" style="width: 5%;">{$number(index)}</div>
        {#each Object.keys(cols) as col}
          <div class="my-cell" style=" width: {cols[col].width};">
            {value(cols[col].path.split("."), items[index], cols[col].type)}
          </div>
        {/each}
      {/if}
    </div>
    <div slot="footer">
      <InfiniteLoading on:infinite="{infiniteHandler}" />
    </div>
  </VirtualList>
  <hr on:mousedown="{() => (resizing = true)}" style="cursor: {resizing ? 'grabbing' : 'grab'}" />
  {#if current_item && current_item > 0 && details_split > 0}
    <div class="one-item pt-2" style="height: {details_split}px; overflow: hide;">
      {#each Object.keys(items[current_item]) as key}
        <span class="w-50" style="text-align: right;"><strong>{key}: </strong></span>
        <span class="w-50"> <code>{JSON.stringify(items[current_item][key]).trim()}</code> </span>
      {/each}
    </div>
  {/if}
</div>

<style>
  hr {
    color: green;
    background-color: blue;
    height: 5px;
    user-select: none;
    margin: 0;
    /*position: absolute;*/
    /*border: solid 1px gray;*/
  }
  :global(.virtual-list-wrapper) {
    margin: 0 0px;
    background: #fff;
    border-radius: 2px;
    box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 3px 1px -2px rgba(0, 0, 0, 0.2), 0 1px 5px 0 rgba(0, 0, 0, 0.12);
    background: #fafafa;
    font-family: -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
    color: #333;
    -webkit-font-smoothing: antialiased;
  }

  .my-row {
    padding: 0 15px;
    border-bottom: 1px solid #eee;
    box-sizing: border-box;
    line-height: 25px;
    font-weight: 500;
    background: #fff;
    display: flex;
    justify-content: space-between;
    cursor: pointer;
  }

  .my-row:hover {
    background-color: #ddd;
  }

  .current {
    background-color: yellowgreen;
  }

  .my-cell {
    display: inline;
    /*border: 1px solid orange;*/
  }
</style>
