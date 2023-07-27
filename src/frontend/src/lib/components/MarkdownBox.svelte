<script lang="ts">
  export let title: string;
  export let content: string;
</script>

<div class="markdown-box">
  <div class="header">
    <b>{title}</b>
  </div>
  <div class="content">
    {content}
  </div>
</div>

<style>
  .markdown-box {
    margin: 20px auto 20px auto;
  }
</style>
