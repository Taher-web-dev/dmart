<script>
  import { Navbar, NavbarBrand } from "sveltestrap";
  let classes = "";
  export { classes as class };
</script>

<Navbar {...$$restProps} class="{'py-0 px-2 ' + classes}" color="light" lighti>
  <NavbarBrand href="/">my Navbar</NavbarBrand>
</Navbar>
