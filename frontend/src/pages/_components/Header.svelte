<script>
  import { Form, Input, Button, Navbar, NavbarBrand, Nav, NavLink } from "sveltestrap";
  import { _, locale } from "../../i18n";
  import { website } from "../../space_config";
  import signedin_user from "../managed/_stores/signedin_user.js";
  import { redirect } from "@roxi/routify";
  import LocalizedValue from "./LocalizedValue.svelte";

  let search;
  function handleClick() {
    event.preventDefault();
    $redirect(`/search/posts?q=${encodeURI(search)}`);
  }

  let localized_displayname;
  $: {
    // console.log("Signed in user", $signedin_user);
    if ($signedin_user) {
      if ($signedin_user.attributes && $signedin_user.attributes.localized_displaynames) {
        localized_displayname = $signedin_user.attributes.localized_displaynames[$locale];
      } else if ($signedin_user.displayname) {
        localized_displayname = $signedin_user.displayname;
      } else {
        localized_displayname = $signedin_user.shortname;
      }
    } else {
      localized_displayname = "";
    }
  }
</script>

<Navbar color="light" light expand="md" class="px-2 w-100 py-0">
  <NavbarBrand href="/"><LocalizedValue field="{website.short_name}" /></NavbarBrand>
  <Nav class="me-auto" navbar>
    {#if $signedin_user}
      <NavLink href="/managed/folder/posts">{localized_displayname}</NavLink>
    {/if}
    <NavLink href="/about">{$_("about")}</NavLink>
    <NavLink href="/contact">{$_("contact_us")}</NavLink>
    {#if !$signedin_user}
      <NavLink href="/managed">{$_("login")}</NavLink>
    {/if}
  </Nav>
  <Form inline="true" class="ms-auto d-flex my-2 my-lg-0">
    <Input
      bsSize="sm"
      type="search"
      readonly="{false}"
      placeholder="{$_('searching_for_what')}"
      class=" ms-sm-2 "
      bind:value="{search}"
      tag="input" />
    <Button size="sm" outline="true" color="secondary" class="ms-2 my-2 my-sm-0 " on:click="{handleClick}">
      {$_("search")}
    </Button>
  </Form>
</Navbar>
