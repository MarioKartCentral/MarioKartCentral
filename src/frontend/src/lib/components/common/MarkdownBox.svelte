<script lang="ts">
  import SvelteMarkdown from 'svelte-markdown';
  export let content: string;
</script>

<div class="markdown-box">
  <div class="content">
    <SvelteMarkdown source={content} />
  </div>
</div>

<style lang="postcss">
  .markdown-box :global(p) {
    display: block;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
  }
  .markdown-box :global(h1) {
    display: block;
    font-size: 2em;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .markdown-box :global(h2) {
    display: block;
    font-size: 1.5em;
    margin-top: 0.83em;
    margin-bottom: 0.83em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .markdown-box :global(h3) {
    display: block;
    font-size: 1.17em;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .markdown-box :global(h4) {
    display: block;
    margin-top: 1.33em;
    margin-bottom: 1.33em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .markdown-box :global(h5) {
    display: block;
    font-size: 0.83em;
    margin-top: 1.67em;
    margin-bottom: 1.67em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .markdown-box :global(h6) {
    display: block;
    font-size: 0.67em;
    margin-top: 2.33em;
    margin-bottom: 2.33em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .markdown-box :global(b) {
    font-weight: bold;
  }
  .markdown-box :global(i) {
    font-style: italic;
  }
  .markdown-box :global(em) {
    font-style: italic;
  }
  .markdown-box :global(a:link) {
    color: #03c744;
    text-decoration: underline;
  }
  .markdown-box :global(a:visited) {
    color: #05773e;
    text-decoration: underline;
  }
  .markdown-box :global(ol) {
    display: block;
    list-style-type: decimal;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
    padding-left: 40px;
  }
  .markdown-box :global(ul) {
    display: block;
    list-style-type: disc;
    margin-top: 1em;
    margin-bottom: 1 em;
    margin-left: 0;
    margin-right: 0;
    padding-left: 40px;
  }
  .markdown-box :global(li) {
    display: list-item;
  }
</style>
