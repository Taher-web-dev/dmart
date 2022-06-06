<script>
  import { Label, Button, Form, FormGroup, Row, Col } from "sveltestrap";
  import { createEventDispatcher } from "svelte";
  import Captcha from "./Captcha.svelte";
  import { _ } from "../../i18n";
  const dispatch = createEventDispatcher();

  export let captcha = false;
  let valid_captcha = false;
  export let title = "";
  function onSubmit(event) {
    event.preventDefault();
    if (captcha && !valid_captcha) {
      alert("Kindly fill captcha properly");
      return;
    }

    const fd = new FormData(event.target);
    //console.log("Event: ", event.target[1]);
    //console.log("Email: ", fd.get("email"));
    let record = {};
    for (var pair of fd.entries()) {
      //console.log("key ", pair[0], "value: ", pair[1]);
      record[pair[0]] = pair[1];
    }
    //console.log("Form data: ", fd);
    dispatch("response", record);
  }

  // novalidate
  // was-validated
  // needs-validation
</script>

<Form on:submit="{onSubmit}" class="needs-validation">
  {#if title && title.length != 0}
    <Row form="{true}">
      <Col class="text-center">
        <h4>{title}</h4>
      </Col>
    </Row>
  {/if}
  <slot />
  {#if captcha}
    <Captcha bind:valid="{valid_captcha}" />
  {/if}
  <Row form="{true}">
    <Col class="text-center">
      <Button outline type="submit">{$_("submit")}</Button>
    </Col>
  </Row>
</Form>
