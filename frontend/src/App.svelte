<script>
  import { setupI18n, dir } from "./i18n";
  import { Router } from "@roxi/routify";
  import { routes } from "../.routify/routes";

  setupI18n(); 
  $: { 
    try {
		document.dir = $dir; 
      //let head = document.getElementsByTagName('HEAD')[0];
		
      //let bootstrap = document.getElementById("bootstrap");
      // if(bootstrap) { head.removeChild(old_bootstrap); }
      //let bootstrap = document.createElement('link');
      //bootstrap.id = "bootstrap";
      //bootstrap.rel = 'stylesheet';
      //bootstrap.type = 'text/css';

      //let fonts = document.getElementById("fonts");
    // if(old_fonts) { head.removeChild(old_fonts); }
    // let fonts = document.createElement('link');
      //fonts.id = "fonts";
      //fonts.rel = 'stylesheet';
      //fonts.type = 'text/css';

		if($dir == "rtl") {
      document.head.children["bootstap"].href="/bootstrap.rtl.min.css"
      document.head.children["fonts"].href="/fonts/rtl_fonts.css";
      //bootstrap.href =
      //document.getElementById("bootstrap").href = '/bootstrap.rtl.min.css';
      // fonts.href=
      //document.getElementById("fonts").href = '/fonts/rtl_fonts.css';
		} else {
      document.head.children["bootstap"].href="/bootstrap.min.css"
      document.head.children["fonts"].href="/fonts/fonts.css";
      //document.getElementById("bootstrap").href = '/bootstrap.min.css';
      //document.getElementById("fonts").href = '/fonts/fonts.css';
		}

      // head.appendChild(bootstrap);
      // head.appendChild(fonts);
    } catch (error) {
      console.log("Error in App:", error)
    }
	}
</script>

<style  global>
  @import "../assets/global.css";
  @import "../assets/bootstrap-icons";
</style>

<Router {routes} />
