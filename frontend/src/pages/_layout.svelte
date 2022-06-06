<!-- routify:options preload="proximity" -->
<script>
  import { Col, Container, Row } from "sveltestrap";
  import Header from "./_components/Header.svelte";
  import Sidebar from "./_components/Sidebar.svelte";
  import Footer from "./_components/Footer.svelte";
</script>

<Container fluid="{false}" class="d-flex flex-column position-relative p-0 my-1">
  <Row class="align-items-start w-100 ms-0" noGutters>
    <Col sm="12"><Header /></Col>
  </Row>
  <Row class="w-100 ms-0 my-1" noGutters>
    <Col sm="2" class=""><Sidebar /></Col>
    <Col sm="10" class=""><slot /></Col>
  </Row>
  <Row class="align-items-end w-100 ms-0 my-1" noGutters>
    <Col sm="12" class=""><Footer /></Col>
  </Row>
</Container>
