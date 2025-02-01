<script lang="ts">
    import MarkdownBox from "./MarkdownBox.svelte";

    export let name: string;
    export let value: string;
    export let disabled = false;
</script>

<div>
    <textarea name={name} bind:value={value} {disabled} on:change/>
</div>
<div>Preview</div>
<div class="preview">
    {#key value}
        <MarkdownBox content={value} />
    {/key}
</div>

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
    min-height: 200px;
  }
</style>