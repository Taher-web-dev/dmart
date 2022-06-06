<script>
  import MarkdownIt from "markdown-it";
  const markdown = new MarkdownIt();

  export let content;

  // Render to an html string
  const rendered = markdown.render(content);
</script>

<div>{@html rendered}</div>
