<script>
  import ListView from "../_components/ListView.svelte";
  import signedin_user from "../_stores/signedin_user";
  import { _ } from "../../../i18n";

  let query = {
    query_type: "logs",
    subpath: "/members/",
    resource_types: ["event"],
    resource_shortnames: [$signedin_user.shortname],
    search: "",
    limit: 10,
    offset: 0,
  };
  let cols = {
    shortname: {
      path: "shortname",
      title: $_("shortname"),
      type: "string",
      width: "15%",
    },
    time: {
      path: "timestamp",
      title: $_("time"),
      type: "timestamp",
      width: "23%",
    },
    event: {
      path: "attributes.event_type",
      title: $_("event"),
      type: "string",
      width: "7%",
    },
    status: {
      path: "attributes.results-status",
      title: $_("status"),
      type: "string",
      width: "10%",
    },
    duration: {
      path: "attributes.duration",
      title: $_("duration"),
      type: "number",
      width: "10%",
    },
    attributes: {
      path: "attributes.results-attributes",
      title: $_("attributes"),
      type: "json",
      width: "30%",
    },
  };
</script>

<ListView query="{query}" cols="{cols}" details_split="{0}" />
