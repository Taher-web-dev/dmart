<script>
  import Form from "./Form.svelte";
  import Input from "./Input.svelte";
  import { _ } from "../../i18n";
  import { dmart_pub_submit } from "../../dmart";
  import { Alert } from "sveltestrap";
  let response = false;
  async function handleResponse(event) {
    let formdata = event.detail;
    let attributes = {
      description: formdata.message,
      name: formdata.name,
      email: formdata.email,
    };

    if (formdata.subject) attributes.displayname = formdata.subject;

    let resp = await dmart_pub_submit("feedback", "feedback", null, attributes);
    console.log("Resp: ", resp.results);
    response = true;
  }
</script>

{#if response}
  <Alert color="success" isOpen="{response}" toggle="{() => (response = false)}">Your feedback was sumitted.</Alert>
{:else}
  <Form title="{$_('contact_form')}" on:response="{handleResponse}" captcha>
    <Input id="name" type="text" title="{$_('name')}" required />
    <Input id="email" type="email" title="{$_('email')}" required />
    <Input id="subject" type="text" title="{$_('subject')}" />
    <Input id="message" type="textarea" title="{$_('message')}" required />
  </Form>
{/if}
