<script>
  import { Container, Row, Col } from "sveltestrap";
  import { createEventDispatcher } from "svelte";
  import {marked} from "marked";
  /*
  import MarkdownIt from 'markdown-it';
  import hljs from 'highlight.js';
  import emoji_plugin from 'markdown-it-emoji';
  import mark_plugin from 'markdown-it-mark';
  import footnote_plugin from 'markdown-it-footnote';
  import deflist_plugin from 'markdown-it-deflist';
  import abbr_plugin from 'markdown-it-abbr';
  import container_plugin from 'markdown-it-container';
  import tasklist_plugin from 'markdown-it-task-lists';
   */
  const dispatch = createEventDispatcher();

  export let content;
  /*
  const markdown = new MarkdownIt({
      html: false,
      xhtmlOut: true,
      breaks: true,
      highlight: function (str, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(lang, str).value
        } catch (e) {
          // eslint-disable-next-line no-console
          console.error('Failed to highlight string')
        }
      }
      return '' // use external default escaping
    },
  }).use(emoji_plugin).use(mark_plugin).use(footnote_plugin).use(deflist_plugin).use(abbr_plugin).use(container_plugin, 'alert-success').use(tasklist_plugin, {enabled: true});

  markdown.renderer.rules.table_open = function() { return '<table class="table table-striped">'; };
  */
</script>

<Container fluid="{true}" class="h-100 pt-1">
  <Row class="h-100">
    <Col sm="6" class="h-100">
      <textarea
        maxlength="4096"
        class="h-100 w-100 m-0 font-monospace form-control form-control-sm"
        bind:value="{content}"
        on:input="{() => dispatch('changed')}"></textarea>
    </Col>
    <Col sm="6" class="h-100">
      <div class="h-100 w-100" style="overflow: hidden auto">
        {@html marked(content)}
      </div>
    </Col>
  </Row>
</Container>

<style global>
  /*@import "highlight.js/styles/a11y-light.css";*/
</style>
