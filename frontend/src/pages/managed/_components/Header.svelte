<script>
  import { Nav, NavItem, NavLink, Navbar, Form, InputGroup, Input, InputGroupText } from "sveltestrap";
  import Icon from "../../_components/Icon.svelte";
  import { _ } from "../../../i18n";
  import SelectLanguage from "./SelectLanguage.svelte";
  import signedin_user from "../_stores/signedin_user.js";
  import { url } from "@roxi/routify";
  import { active_section } from "../_stores/active_section.js";
  import sections from "../_stores/sections.js";
</script>

<Navbar class="py-0 px-1">
  <Nav tabs class="align-items-center w-100" style="background-color: #f4f4f4;">
    {#each $sections as section}
      <NavItem>
        <NavLink
          href="{$url('/managed/' + section.name)}"
          title="{$_(section.name)}"
          on:click="{() => {
            $active_section = section;
          }}"
          active="{$active_section.name == section.name}">
          <Icon name="{section.icon}" />
          {#if section.notifications > 0}
            <span class="badge rounded-pill bg-danger custom-badge">{section.notifications}</span>
          {/if}
        </NavLink>
      </NavItem>
    {/each}
    <NavItem
      ><NavLink href="/" title="{$_('published')}">
        <Icon name="globe" />
      </NavLink></NavItem>
    <NavItem><SelectLanguage /></NavItem>
    <NavItem
      ><NavLink href="#" title="{$_('logout')}" on:click="{signedin_user.logout}">
        <Icon name="power" />
      </NavLink></NavItem>
    <Form inline="true" class="ms-auto ">
      <InputGroup size="sm">
        <Input placeholder="{$_('searching_for_what')}" />
        <InputGroupText><Icon name="search" /></InputGroupText>
      </InputGroup>
    </Form>
  </Nav>
</Navbar>

<style>
  .custom-badge {
    position: relative;
    right: 0.5rem;
    top: -0.5rem;
    border: 2px solid #fff;
    font-size: 0.6rem;
  }
</style>
