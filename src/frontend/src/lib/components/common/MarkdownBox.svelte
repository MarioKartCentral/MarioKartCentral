<script lang="ts">
  import SvelteMarkdown from 'svelte-markdown';
  export let content: string;
</script>

<div class="markdown-box">
  <div class="content">
    <SvelteMarkdown source={content} />
  </div>
</div>
