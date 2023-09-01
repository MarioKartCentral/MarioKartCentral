<script lang="ts">
  export let href: string | null = null;
  export let external: string | null = null;
  export let title: string | null = null;
  export let selected = false;
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
  /* mobile */
  li {
    display: flex;
  }

  a {
    font-weight: bold;
    color: white;
    text-decoration: none;
    flex-grow: 1;
    padding: 10px 0;
  }

  [aria-current] {
    text-decoration: underline;
    text-decoration-thickness: 2px;
    text-underline-offset: 8px;
  }

  /* desktop */
  @media (min-width: 1024px) {
    li {
      flex-direction: column;
    }
    a {
      padding: 0;
    }
  }
</style>
