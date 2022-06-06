<script>
  //import Attachments from "./Attachments.svelte";
  import Tag from "./Tag.svelte";
  import MediaView from "./MediaView.svelte";
  import { url } from "@roxi/routify";
  import { _, date, number } from "../../i18n";
  import { dmart_pub_submit } from "../../dmart";
  import signedin_user from "../managed/_stores/signedin_user.js";
  import { onMount } from "svelte";
  import MarkdownViewer from "./MarkdownViewer.svelte";

  import { website } from "../../space_config";
  import { Button, Badge, CardLink, Card, CardBody, CardText, CardTitle, CardHeader, CardSubtitle } from "sveltestrap";
  import Icon from "./Icon.svelte";
  export let data;
  export let extended = false;
  //console.log("EntryCard: ", data);
  let timestamp = new Date(data.timestamp);
  let displayname;
  let description;
  let tags = [];
  let author;
  let editor;
  let embedded;
  let content_type = "";
  let entryurl;
  if (data.attributes) {
    author = data.attributes.author;
    editor = data.attributes.editor;
    tags = data.attributes.tags;
    if (data.attributes.description) description = data.attributes.description;
    if (data.attributes.displayname) displayname = data.attributes.displayname;
    if (data.attributes.payload && data.attributes.payload.embedded) embedded = data.attributes.payload.embedded;
    if (data.attributes.payload && data.attributes.payload.content_type)
      content_type = data.attributes.payload.content_type;
    if (data.attributes.payload && data.attributes.payload.filepath)
      entryurl = `${website.backend}/media/${website.space_name}/${data.subpath}/entry/${data.attributes.payload.filepath}`;
  }

  function handle(type) {
    //let type = event.target.title;
    //console.log("Type: ", type);
    return function () {
      event.preventDefault();
      event.stopPropagation();
      dmart_pub_submit(type, data.subpath, null, null, data.shortname);
    };
  }

  onMount(() => {});
  /*
	let maindiv;
	let shown = false;
	let changed = false;
	let prehtml;
	function showEditor() {
	  if($signedin_user && extended && !shown) {
		  shown = true;
			let html = maindiv.innerHTML;
			if( !prehtml ) prehtml = html;
			//const Editor = require('cl-editor');
			maindiv.innerHTML = '';
			let editor = new Editor({
				target: maindiv,
				props: {
					//actions: ['b', 'i', 'u', 'h2', 'removeFormat'],
					actions: [
						'viewHtml',
						'undo', 
						'redo', 
						'b', 
						'i', 
						'u', 
						'strike', 
						'sup', 
						'sub', 
						'h1', 
						'h2', 
						'p', 
						'blockquote', 
						'ol', 
						'ul', 
						'hr', 
						'left', 
						'right', 
						'center', 
						'justify', 
						'a', 
						'image', 
						'forecolor', 
						'backcolor', 
						'removeFormat'
					],
					height: 'auto',
					//html: html
				}
			});

			editor.setHtml(html, true);

			//maindiv.firstChild.firstChild.style.fontFamily = "unset";
			maindiv.firstChild.firstChild.style.fontSize = "1rem";

			editor.$on('blur', () => {
				html = editor.getHtml(true);
				editor.$destroy();
				maindiv.innerHTML = html;
				shown = false;
				changed = (prehtml != html);
			});
		}
	}
*/
</script>

<!-- routify:options param-is-page=true -->

<Card class="mb-4">
  <CardHeader class="py-0 ps-0 pe-2">
    <CardTitle class="float-start ps-2 mt-1 mb-1">
      {#if extended}
        {displayname}
      {:else}
        <CardLink
          href="{$url('/entry/:subpath/:shortname', {
            subpath: data.subpath,
            shortname: data.shortname,
          })}"
          title="{$_('more')}">
          {displayname}
        </CardLink>
      {/if}
    </CardTitle>
    <CardTitle class="float-end mb-0 pt-1">
      <Button href="#" title="Media" size="sm" outline>
        <Icon name="paperclip" />
        <Badge color="secondary">{$number(data.attachments.media ? data.attachments.media.length : 0)}</Badge>
      </Button>
      <Button href="#" title="Like" on:click="{handle('like')}" size="sm" color="success" outline>
        <Icon name="heart" />
        <Badge color="secondary">{$number(data.attachments.reaction ? data.attachments.reaction.length : 0)}</Badge>
      </Button>
      <Button href="#" title="Comment" on:click="{handle('comment')}" size="sm" outline>
        <Icon name="reply-all" />
        <Badge color="secondary">{$number(data.attachments.reply ? data.attachments.reply.length : 0)}</Badge>
      </Button>
      <Button href="#" title="Share" on:click="{handle('share')}" size="sm" outline>
        <Icon name="share" />
        <Badge color="secondary">{$number(data.attachments.share ? data.attachments.share.length : 0)}</Badge>
      </Button>
      <Button href="#" title="Report" on:click="{handle('report')}" size="sm" outline>
        <Icon name="exclamation-triangle" />
      </Button>
      {#if $signedin_user && extended}
        <Button href="#" title="Unpublish" on:click="{handle('report')}" size="sm" outline>
          <Icon name="eye" />
        </Button>
      {/if}
    </CardTitle>
  </CardHeader>
  <CardBody class="pb-1">
    <CardText class="border-bottom">
      <!--div bind:this={maindiv} on:click={showEditor}-->
      {#if description}
        {@html description}
      {/if}
      {#if embedded && content_type.startsWith("text/html")}
        {@html embedded}
      {:else if embedded && content_type.startsWith("text/markdown")}
        <MarkdownViewer content="{embedded}" />
      {:else if entryurl}
        <MediaView url="{entryurl}" displayname="{displayname}" content_type="{content_type}" />
      {/if}
    </CardText>
    <CardSubtitle class="">
      <small>
        {#if author}{$_("author")}: {author.shortname} -{/if}
        {#if editor}{$_("editor")}: {editor.shortname} -{/if}
        <Icon name="price-tags" title="Tags" />
        {$_("tags")}:
        {#each tags as one}
          <Tag name="{one}" />
        {/each}
        <Icon name="clock" />
        {$_("edited_at")}:
        <abbr title="{$_('datetime', { values: { ts: timestamp } })}">
          {$date(timestamp, { format: "short" })}
        </abbr>
      </small>
    </CardSubtitle>
  </CardBody>
</Card>

<!--CardFooter>
		<div class="float-left">
        ({$number(data.attachments.reply ? data.attachments.reply.length : 0)})
      - {$_('reactions')} ({$number(data.attachments.reaction ? data.attachments.reaction.length : 0)})
      - {$_('shares')} ({$number(data.attachments.share ? data.attachments.share.length : 0)})
			</div>
    </CardFooter-->
<style>
  :global(.card-body) {
    padding: 0.25rem 0.5rem;
    background-color: ivory;
  }

  :global(.card-text) {
    font-family: "uthmantn";
    font-size: 1.5rem !important;
  }

  :global(.card-title) {
    /*font-family: "uthmantn-bold";*/
    font-weight: 500;
    font-size: 1.25em;
    text-align: center;
    margin-bottom: 0rem;
  }
</style>
