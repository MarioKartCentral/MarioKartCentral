<script lang="ts">
  export let header: string | null = null;
  export let href: string | null = null;
</script>

<div class="section-container">
  {#if header !== null}
    <div class="header bg-primary-800">
      <div class="header_element">
        {#if href}
          <h2><a {href}>{header}</a></h2>
        {:else}
          <h2>{header}</h2>
        {/if}
      </div>
      {#if $$slots.header_content}
        <div class="header_element centered">
          <slot name="header_content" />
        </div>
      {/if}
    </div>
  {/if}
  {#if $$slots.default}
    <div class="wrapper">
      <slot />
    </div>
  {/if}
</div>

<style>
  h2 {
    font-size: 20px;
  }
  .section-container {
    max-width: 1200px;
    margin: 20px auto 20px auto;
    background-color: rgba(255, 255, 255, 0.15);
  }
  .header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    /* background-color: rgba(0, 128, 0, 0.6); */
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
    margin: 5px 10px 5px 10px;
  }
</style>
