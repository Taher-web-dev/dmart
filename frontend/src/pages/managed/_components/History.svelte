<script>
  import Table from "./Table.svelte";
  import { dmart_query } from "../../../dmart.js";
  import { _ } from "../../../i18n";
  //import { ready } from "@roxi/routify";

  export let subpath;
  export let shortname;

  export let scoped = {};
  scoped;
  export let scopedSync = {};
  scopedSync;

  let alterations = [];
  let count = 0;
  let total = 0;
  let status = "";

  let cols = {
    hash: {
      path: "hash",
      title: $_("hash"),
      type: "string",
    },
    current: {
      path: "current",
      title: $_("current"),
      type: "string",
    },
    previous: {
      path: "previous",
      title: $_("previous"),
      type: "string",
    },
    time: {
      path: "timestamp",
      title: $_("time"),
      type: "timestamp",
    },
    /*
    diff: {
      path: "attributes.diff",
      title: $_("details"),
      type: "json",
  },*/
  };

  $: {
    let query = {
      query_type: "history",
      subpath: subpath,
      resource_types: ["alteration"],
      resource_shortnames: [shortname],
      limit: 10,
      offset: 0,
    };
    dmart_query(query)
      .then((json) => {
        alterations = json.records
          .map((one) => {
            one.hash = one.shortname.substring(5, 13);

            if (one.attributes.diff) {
              one.current = `${one.attributes.diff.payload?.bytesize.new}/${one.attributes.new_checksum.substring(
                5,
                13
              )}`;
              one.previous = `${one.attributes.diff.payload?.bytesize.old}/${one.attributes.old_checksum.substring(
                5,
                13
              )}`;
            }
            return one;
          })
          .reverse();
        //alterations = json.records.reverse();
        //console.log(alterations);
        if (json?.results[0].status == "success") {
          count = json.results[0].attributes.returned;
          total = json.results[0].attributes.total;
          status = "success";
        } else {
          status = json?.results[0] || "Unknown error";
        }
      })
      .catch(console.log);
  }
</script>

<h6>Returned {count} out of {total} with status {status}</h6>
<Table cols="{cols}" rows="{alterations}" />
