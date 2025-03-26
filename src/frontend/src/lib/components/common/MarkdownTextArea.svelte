<script lang="ts">
    import MarkdownBox from "./MarkdownBox.svelte";
    import Tabs from "$lib/components/common/tabs/Tabs.svelte";
    import TabItem from "$lib/components/common/tabs/TabItem.svelte";

    export let name: string;
    export let value: string;
    export let disabled = false;
</script>


<Tabs>
  <TabItem open title="Input">
    <div>
        <textarea name={name} bind:value={value} {disabled} on:change/>
    </div>
    <div class="tutorial">
      <a href="https://www.markdownguide.org/basic-syntax/" target="_blank">
        This text input supports Markdown. Click here for a list of basic Markdown syntax.
      </a>
    </div>
  </TabItem>
  <TabItem title="Preview">
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