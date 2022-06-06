<script>
  import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from "sveltestrap";
  import Input from "./Input.svelte";
  import { _ } from "../../i18n";
  import signedin_user from "../managed/_stores/signedin_user.js";
  import Captcha from "./Captcha.svelte";
  import { dmart_content, dmart_pub_submit } from "../../dmart";
  import sha1 from "../../sha1";
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();

  export let open = false;
  export let size = undefined;

  export let subpath;
  export let parent_shortname;

  let name;
  let email;
  let reply;

  function toggle() {
    open = !open;
  }
  function cancel() {
    open = !open;
  }

  async function create() {
    let record = {
      subpath: subpath,
      shortname: "",
      parent_shortname: parent_shortname,
      resource_type: "reply",
      attributes: {
        payload: {
          checksum: `sha1:${sha1(reply)}`,
          embedded: reply,
          content_type: "text/html; charset=utf8",
          bytesize: new Blob([reply]).size,
        },
      },
    };

    let resp;
    if ($signedin_user) {
      console.log("Request: ", record);
      resp = await dmart_content("create", record);
    } else {
      record.attributes.name = name;
      record.attributes.email = email;
      resp = await dmart_pub_submit("anonreply", subpath, parent_shortname, record.attributes);
    }
    console.log("Resp: ", resp.results);
    open = false;
    dispatch("created", record);
  }
</script>

<!--Alert color="success" isOpen={response} toggle={() => (response = false)}>
    Your feedback was sumitted.
    <pre>{JSON.stringify(data)}</pre>
  </Alert-->

<Modal bind:isOpen="{open}" toggle="{toggle}" size="{size}">
  <ModalHeader>{$_("write_a_reply")}</ModalHeader>
  <ModalBody>
    {#if !$signedin_user}
      <Input id="name" type="text" title="{$_('name')}" bind:value="{name}" />
      <Input id="email" type="email" title="{$_('email')}" bind:value="{email}" />
    {/if}
    <!--Input id="subject" type="text" title={$_('subject')} /-->
    <Input id="reply" type="textarea" title="{$_('reply')}" bind:value="{reply}" />
    {#if !$signedin_user}
      <Captcha />
    {/if}
  </ModalBody>
  <ModalFooter>
    <Button color="secondary" on:click="{cancel}">إلغاء</Button>
    <Button color="primary" on:click="{create}">قبول</Button>
  </ModalFooter>
</Modal>
