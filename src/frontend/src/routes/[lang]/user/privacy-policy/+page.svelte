<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { LL, locale } from '$i18n/i18n-svelte';
  import SvelteMarkdown from 'svelte-markdown';

  const files = import.meta.glob('./*.md', {
    query: '?raw',
    import: 'default',
  });

  const filePath = `./${$locale}.md`;
  const file = files[filePath] ?? files['./en-us.md'];
</script>

<Section header={$LL.LEGAL.PRIVACY_POLICY()}>
  <div class="terms space-y-6 text-gray-200">
    {#await file() then terms}
      <SvelteMarkdown source={terms} />
      <div class="mt-8 pt-4 border-t border-gray-700 text-gray-400 text-sm">
        <p><strong>{$LL.LEGAL.LAST_UPDATED()}:</strong> 2025-05-18</p>
      </div>
    {/await}
  </div>
</Section>

<style>
  /* Keep existing styles for compatibility with HTML that may be inserted dynamically */
  .terms :global(p) {
    display: block;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
  }
  .terms :global(h1) {
    display: block;
    font-size: 2em;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .terms :global(h2) {
    display: block;
    font-size: 1.5em;
    margin-top: 0.83em;
    margin-bottom: 0.83em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .terms :global(h3) {
    display: block;
    font-size: 1.17em;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
    color: rgb(209, 213, 219);
  }
  .terms :global(h4) {
    display: block;
    margin-top: 1.33em;
    margin-bottom: 1.33em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .terms :global(h5) {
    display: block;
    font-size: 0.83em;
    margin-top: 1.67em;
    margin-bottom: 1.67em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .terms :global(h6) {
    display: block;
    font-size: 0.67em;
    margin-top: 2.33em;
    margin-bottom: 2.33em;
    margin-left: 0;
    margin-right: 0;
    font-weight: bold;
  }
  .terms :global(b) {
    font-weight: bold;
  }
  .terms :global(i) {
    font-style: italic;
  }
  .terms :global(em) {
    font-style: italic;
  }
  .terms :global(a:link) {
    color: #4dabf7;
    text-decoration: underline;
  }
  .terms :global(a:visited) {
    color: #74c0fc;
    text-decoration: underline;
  }
  .terms :global(ol) {
    display: block;
    list-style-type: decimal;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0;
    margin-right: 0;
    padding-left: 40px;
  }
  .terms :global(ul) {
    display: block;
    list-style-type: disc;
    margin-top: 1em;
    margin-bottom: 1 em;
    margin-left: 0;
    margin-right: 0;
    padding-left: 40px;
  }
  .terms :global(li) {
    display: list-item;
  }
</style>
