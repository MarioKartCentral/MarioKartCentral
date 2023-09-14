<script lang="ts">
  export let header: string | null = null;
</script>

<div class="container">
  {#if header}
    <div class="header">
      <div class="header_element">
        <h2>{header}</h2>
      </div>
      {#if $$slots.header_content}
        <div class="header_element centered">
          <slot name="header_content" />
        </div>
      {/if}
    </div>
  {/if}
  <div class="wrapper">
    <slot />
  </div>
</div>

<style>
  .container {
    width: 65%;
    margin: 20px auto 20px auto;
    background-color: rgba(255, 255, 255, 0.15);
  }
  .header {
    display: grid;
    grid-template-columns: 3fr 1fr;
    background-color: rgba(0, 128, 0, 0.6);
  }
  .centered {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .wrapper {
    padding: 10px;
  }
  div.header_element {
    margin: 5px;
  }
</style>
