<script lang="ts">
  import MarkdownBox from './MarkdownBox.svelte';
  import Tabs from '$lib/components/common/tabs/Tabs.svelte';
  import TabItem from '$lib/components/common/tabs/TabItem.svelte';
  import LL from '$i18n/i18n-svelte';

  export let name: string;
  export let value: string;
  export let disabled = false;
</script>

<Tabs>
  <TabItem open title={$LL.MARKDOWN.INPUT()}>
    <div>
      <textarea {name} bind:value {disabled} on:change />
    </div>
    <div class="tutorial">
      <a href="https://www.markdownguide.org/basic-syntax/" target="_blank">
        {$LL.MARKDOWN.MARKDOWN_HELP()}
      </a>
    </div>
  </TabItem>
  <TabItem title={$LL.MARKDOWN.PREVIEW()}>
    <div class="preview">
      {#key value}
        <MarkdownBox content={value} />
      {/key}
    </div>
  </TabItem>
</Tabs>

<style>
  textarea {
    min-width: 50%;
    width: 100%;
    height: 200px;
  }
  textarea:disabled {
    background-color: #ccc;
  }
  div.preview {
    border: 1px solid white;
    padding: 10px;
    min-height: 250px;
    max-height: 250px;
    overflow: scroll;
  }
  div.tutorial {
    color: lightgray;
  }
</style>
