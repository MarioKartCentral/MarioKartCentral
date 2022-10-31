<script lang="ts">
    export let href : string | null = null;
    export let external : string | null = null;
    export let title : string | null  = null;
    export let selected : boolean = false;
</script>

<li>
  {#if external}
    <a href={external} {title} rel="external">
      <slot />
    </a>
  {:else}
    <a aria-current={selected ? 'page' : undefined} {href} {title}>
      <slot />
    </a>
  {/if}
</li>

<style>
  li {
    display: flex;
    align-items: center;
  }
  
  a {
    font-weight: bold;
    color: white;
    text-decoration: none;
  }

  [aria-current] {
    text-decoration: underline;
    text-decoration-thickness: 2px;
    text-underline-offset: 8px;
  }
</style>