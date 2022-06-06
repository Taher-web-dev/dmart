<script>
  import { fade, fly } from "svelte/transition";
  import { Container, Row, Col, TabContent, TabPane } from "sveltestrap";
  import { dmart_pub_query } from "../../dmart.js";
  import { leftover } from "@roxi/routify";
  import { onMount, onDestroy } from "svelte";
  import MediaView from "../_components/MediaView.svelte";
  import MarkdownViewer from "../_components/MarkdownViewer.svelte";
  import { website } from "../../space_config";
  import { _, number } from "../../i18n";

  onMount(() => {
    document.addEventListener("touchstart", touchEv, false);
    document.addEventListener("touchmove", touchEv, false);
    document.addEventListener("touchend", touchEv, false);
  });

  onDestroy(() => {
    document.removeEventListener("touchstart", touchEv, false);
    document.removeEventListener("touchmove", touchEv, false);
    document.removeEventListener("touchend", touchEv, false);
  });

  //let isOpen = false;
  let items = [];
  let folder = { attributes: {} };
  let available = 0;
  let resourceTypes = ["folder", "post", "locator", "biography", "contact", "media"];
  let subpath = decodeURI($leftover);
  if (subpath.startsWith("/")) subpath = subpath.slice(1);
  if (subpath.endsWith("/")) subpath = subpath.slice(0, -1);

  let active;
  let currentIndex = 0;

  //let fragments = document.URL.split("#");
  //if (fragments.length>1)
  //	active = decodeURI(fragments[1]);
  if (location.hash) active = location.hash.substring(1);

  //console.log("Subpath: ", subpath);
  dmart_pub_query(subpath, resourceTypes, [], "subpath", "*", 30, 0)
    .then((resp) => {
      items = resp.records;
      //console.log("Items before sort: ", items);
      items.sort((a, b) => {
        if (a && a.attributes && a.attributes.ordinal && b && b.attributes && b.attributes.ordinal) {
          //console.log("A: ", a.shortname, a.attributes.ordinal, "B: ", b.shortname, b.attributes.ordinal);
          //return (a.attributes.ordinal > b.attributes.ordinal)?1:(a.attributes.ordinal < b.attributes.ordinal)?-1:0;
          return a.attributes.ordinal - b.attributes.ordinal;
        } else {
          return a && a.attributes && a.attributes.ordinal ? -1 : 1;
        }
      });

      currentIndex = 0;

      for (var i = 0; i < items.length; i++) {
        if (items[i].shortname == active) currentIndex = i;
      }

      active = items[currentIndex].shortname;
      folder = resp.included[0];
      available = resp.results[0].attributes.total;
    })
    .catch(console.log);

  let key;
  //let keyCode;
  function handleKeydown(event) {
    key = event.key;
    // console.log(key);
    //keyCode = event.keyCode;

    /*let currentIndex = 0;
		for(var i = 0; i < items.length; i++) {
			if(active == items[i].shortname) {
				currentIndex = i;
				break;
			}
		}*/

    if (["ArrowRight", "ArrowDown", " "].includes(key) && currentIndex < items.length - 1) {
      active = items[++currentIndex].shortname;
    } else if (["ArrowLeft", "ArrowUp"].includes(key) && currentIndex > 0) {
      active = items[--currentIndex].shortname;
    }
  }

  // $: console.log(currentIndex);
  let footerHeight;
  let headerHeight;

  function handleSwipe(event) {
    console.log(event);
    // alert(JSON.stringify(event));
    // Example output:
    // { type: 'swipe', originalEvent: [TouchEvent], direction: 'left', axis: 'x' }
  }

  let touch_start = { x: 0, y: 0 };
  let touch_end = { x: 0, y: 0 };
  function touchEv(event) {
    if (!items || items.lenth < 1) reutrn;

    var touch = event.changedTouches[0];
    switch (event.type) {
      case "touchstart":
        touch_start.x = touch.clientX;
        touch_start.y = touch.clientY;
        break;
      case "touchend":
        touch_end.x = touch.clientX;
        touch_end.y = touch.clientY;
        break;
      case "touchmove":
      default:
        return;
    }

    var xDiff = touch_start.x - touch_end.x;
    var yDiff = touch_start.y - touch_end.y;
    if (Math.abs(xDiff) > Math.abs(yDiff)) {
      // most significant
      if (xDiff > 0) {
        // left swipe
        if (currentIndex > 0) active = items[--currentIndex].shortname;
      } else {
        // right swipe
        if (currentIndex < items.length - 1) active = items[++currentIndex].shortname;
      }
    } else {
      if (yDiff > 0) {
        // up swipe
        if (currentIndex > 0) active = items[--currentIndex].shortname;
      } else {
        // down swipe
        if (currentIndex < items.length - 1) active = items[++currentIndex].shortname;
      }
    }
    event.preventDefault();
  }
</script>

<svelte:window on:keydown="{handleKeydown}" />

<div on:swipe="{handleSwipe}">
  <Container class="h-100 border border-info " fluid="{true}">
    <div bind:clientHeight="{headerHeight}">
      <Row class="border-success mt-2">
        <Col class="text-center">
          <span class="h3">
            {folder.attributes.displayname}
            <!--b>i</b>nformation <b>m</b>anagement and e<b>x</b>change-->
          </span>
          :
          <span class="h5"> {@html folder.attributes.description} <!--A unified data platform--> </span>
          <hr />
        </Col>
      </Row>
    </div>
    <Row class="py-0 " style="height: calc(100% - {headerHeight + footerHeight}px);">
      <Col class="h-100 px-4">
        <TabContent class="" activeTab="{active}">
          {#each items as slide, i}
            {#if active == slide.shortname}
              <TabPane show="{i == 0}" fade class="" tabId="{slide.shortname}">
                <div in:fly="{{ y: 200, duration: 2000 }}" out:fade>
                  <h4 id="{slide.shortname}">{$number(slide.attributes.ordinal)}. {slide.attributes.displayname}</h4>
                  {#if slide.attributes.payload.embedded && slide.attributes.payload.content_type.startsWith("text/html")}
                    {@html slide.attributes.payload.embedded}
                  {:else if slide.attributes.payload.embedded && slide.attributes.payload.content_type.startsWith("text/markdown")}
                    <MarkdownViewer value="{slide.attributes.payload.embedded}" />
                  {:else}
                    <MediaView
                      url="{`${website.backend}/media/${website.space_name}/${slide.subpath}/entry/${slide.attributes.payload.filepath}`}"
                      displayname="{slide.attributes.displayname}"
                      content_type="{slide.attributes.payload.content_type}" />
                  {/if}
                </div>
              </TabPane>
            {/if}
          {/each}
        </TabContent>
      </Col>
    </Row>
    <div bind:clientHeight="{footerHeight}" class="fixed-bottom">
      <Row class="border align-items-end align-self-end py-2">
        <Col class="text-start ps-4">
          <kbd>{key === " " ? "Space" : key}</kbd>
        </Col>

        <Col class="text-center">
          {active}
        </Col>
        <Col class=" text-end pe-4">
          <small>
            {$_("page_of_total", { values: { page: $number(currentIndex + 1), total: $number(items.length) } })}
          </small>
        </Col>
      </Row>
    </div>
  </Container>
</div>
