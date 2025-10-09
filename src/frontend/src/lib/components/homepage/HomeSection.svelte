<script lang="ts">
  export let header: string | null = null;
  export let linkText: string | null = null;
  export let link: string | null = null;
  export let style: string | null = null;
</script>

<div class="container" {style}>
  {#if header}
    <div class="header bg-primary-800">
      <div class="header_element">
        {#if link}
          <h2><a href={link}>{header}</a></h2>
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
      <div>
        <slot />
      </div>
      <div class="mt-[10px] mb-[5px] h-[20px] text-center">
        {#if link && linkText}
          <a class="p-1 font-medium" href={link}>
            {linkText}
          </a>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  h2 {
    font-size: 20px;
  }
  .container {
    max-width: 1200px;
    height: calc(100% - 40px);
  }
  .header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }
  .centered {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .wrapper {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: rgba(255, 255, 255, 0.15);
    padding: 10px;
    height: 100%;
  }
  div.header_element {
    margin: 5px 10px 5px 10px;
  }
</style>
