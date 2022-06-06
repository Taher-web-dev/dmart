<script>
  import { Container, Row, Col } from "sveltestrap";
  import Header from "./_components/Header.svelte";
  import Sidebar from "./_components/Sidebar.svelte";
  import signedin_user from "./_stores/signedin_user.js";
  import Login from "./_components/Login.svelte";
  import sections from "./_stores/sections.json";
  import { active_section } from "./_stores/active_section.js";
  import { leftover, ready } from "@roxi/routify";
  import Notifications from "svelte-notifications";

  let window_height;
  let header_height;

  export let scoped;
  scoped;
  export let scopedSync;
  scopedSync;

  //console.log("leftover", $leftover, "active section name", $active_section);
  if ($leftover && !$leftover.startsWith($active_section.name)) {
    for (let section of sections) {
      //console.log("Comparing ", $leftover, section.name);
      if ($leftover.startsWith(section.name)) {
        $active_section = section;
        //console.log(`Setting active section to ${section.name}.`); //Page title: ${page.title}`);
        break;
      }
    }
  }

  $ready();
</script>

<svelte:window bind:innerHeight="{window_height}" />

<Notifications>
  {#if !$signedin_user}
    <div class="container-fluid d-flex align-items-start" id="login-container" style="height: {window_height - 9}px; ">
      <Login />
    </div>
  {:else}
    <div bind:clientHeight="{header_height}" class="fixed-top"><Header /></div>
    <!--border border-secondary-->
    <Container
      fluid="{true}"
      id="mymain"
      class="position-relative p-0"
      style="top: {header_height}px; height: {window_height - header_height - 8}px;">
      <Row class="h-100" noGutters>
        <Col sm="2" class="h-100 border-end border-light px-1">
          <Sidebar />
        </Col>
        <Col sm="10" class="h-100 border-start border-light px-1">
          <slot />
        </Col>
      </Row>
    </Container>
  {/if}
</Notifications>

<style>
  #login-container {
    background-color: #fafaf6;
  }
</style>
