<script>
  import Table from "../_components/Table.svelte";
  import { dmart_query } from "../../../dmart.js";
  import { _ } from "../../../i18n";
  import signedin_user from "../_stores/signedin_user";
  import { status_line } from "../_stores/status_line.js";

  import { ready } from "@roxi/routify";
  import { onDestroy } from "svelte";

  onDestroy(() => status_line.set(""));

  export let scoped;
  scoped;
  export let scopedSync;
  scopedSync;

  let events = [];
  let count = 0;
  let total = 0;
  let api_status = "";

  let query = {
    query_type: "logs",
    subpath: "/members/",
    resource_types: ["event"],
    resource_shortnames: [$signedin_user.shortname],
    limit: 100,
    offset: 0,
  };

  let cols = {
    shortname: {
      path: "shortname",
      title: $_("shortname"),
      type: "string",
    },
    time: {
      path: "timestamp",
      title: $_("time"),
      type: "timestamp",
    },
    event: {
      path: "attributes.event_type",
      title: $_("event"),
      type: "string",
    },
    status: {
      path: "attributes.results-status",
      title: $_("status"),
      type: "string",
    },
    duration: {
      path: "attributes.duration",
      title: $_("duration"),
      type: "number",
    },
    attributes: {
      path: "attributes.results-attributes",
      title: $_("attributes"),
      type: "json",
    },
  };

  dmart_query(query)
    .then((json) => {
      events = json.records
        .map((one) => {
          delete one.attributes["results-attributes"].backtrace;
          delete one.attributes["results-attributes"].auth_token;
          return one;
        })
        .reverse();
      if (json?.results[0].status == "success") {
        count = json.results[0].attributes.returned;
        total = json.results[0].attributes.total;
        api_status = "success";
        status_line.set(`Loaded ${count} of ${total}.<br/>api: ${api_status}`);
      } else {
        api_status = json?.results[0] || "Unknown error";
        status_line.set(`api: ${api_status}`);
      }
      $ready();
    })
    .catch(console.log);
</script>

<Table cols="{cols}" rows="{events}" />

<!--
{#each events as event}
<pre><code>{JSON.stringify(event, undefined, 1)}</code></pre>
<hr />
{/each}
-->
