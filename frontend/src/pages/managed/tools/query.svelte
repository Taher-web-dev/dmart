<script>
  // import Code from "../../../components/Code.svelte";
  import Table from "../_components/Table.svelte";
  import { _ } from "../../../i18n";
  import { TabPane, TabContent, Nav, NavItem, NavLink } from "sveltestrap";
  import { Container, Row, Col } from "sveltestrap";
  import QueryForm from "../_components/QueryForm.svelte";
  import { onMount } from "svelte";

  let Prism;
  onMount(async () => {
    const prismModule = await import("svelte-prismjs");
    await import("prismjs/components/prism-json.js");
    Prism = prismModule.default;
  });

  //import hljs from "highlight.js";
  //import json from "highlight.js/lib/languages/json";

  export let scoped;
  scoped;
  export let scopedSync;
  scopedSync;

  //hljs.registerLanguage("json", json);

  let results = {};
  let rows = [];
  let highlighted = "";

  function handleResponse(event) {
    //console.log("Response: ", event.detail);
    results = event.detail;
    rows = results.records;
    highlighted = JSON.stringify(results, undefined, 1); //hljs.highlight("json", JSON.stringify(results, undefined, 1)).value;
  }

  let cols = {
    shortname: {
      path: "shortname",
      title: $_("shortname"),
      type: "string",
    },
    displayname: {
      path: "attributes.displayname",
      title: $_("displayname"),
      type: "string",
    },
    tags: {
      path: "attributes.tags",
      title: $_("tags"),
      type: "string",
    },
    payload: {
      path: "attributes.payload.embedded",
      title: $_("payload"),
      type: "string",
    },
    is_active: {
      path: "attributes.is_active",
      title: $_("is_active"),
      type: "string",
    },
  };

  let myactive = "original";
</script>

<Container fluid="{true}" class="h-100">
  <Row class="h-100" noGutters>
    <Col sm="2" class="h-100">
      <QueryForm on:response="{handleResponse}" />
    </Col>
    <Col sm="10" class="h-100 d-flex flex-column">
      <Nav tabs>
        <NavItem
          ><NavLink href="#" on:click="{() => (myactive = 'original')}" active="{myactive == 'original'}"
            >{$_("raw")}</NavLink
          ></NavItem>
        <NavItem
          ><NavLink href="#" on:click="{() => (myactive = 'tabular')}" active="{myactive == 'tabular'}"
            >{$_("tabular")}</NavLink
          ></NavItem>
      </Nav>
      <div class="flex-grow-0 overflow-y-auto" style="min-height: 0;">
        <TabContent class="h-100" activeTab="{myactive}">
          <TabPane class="h-100" tabId="tabular">
            <Table cols="{cols}" rows="{rows}" />
          </TabPane>
          <TabPane class="h-100" tabId="original">
            <!--pre
              class="h-100 mx-2 hljs mb-0"
              style="direction: ltr; text-align: left; white-space: pre-wrap; overflow-y: scroll; overflow-x: hidden;">
                <code>{@html highlighted}</code> 
              </pre-->
            <svelte:component
              this="{Prism}"
              classes="h-100 mx-2 m-0 overflow-auto"
              style="direction: ltr; font-size: 0.8rem;">
              {highlighted}
            </svelte:component>
          </TabPane>
        </TabContent>
      </div>
    </Col>
  </Row>
</Container>

<style global>
  /*@import "prismjs/plugins/line-numbers/prism-line-numbers.css";
  @import "prismjs/plugins/command-line/prism-command-line.css";
  @import "prismjs/plugins/line-highlight/prism-line-highlight.css";*/
  @import "prismjs/themes/prism.css";
  @import "prismjs/themes/prism-coy.css";
  /*code { white-space: pre-wrap; }*/
  pre[class*="language-"],
  code[class*="language-"] {
    white-space: pre-wrap;
  }
</style>
