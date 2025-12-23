<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  export let root: HTMLElement | null = null;

  let el: HTMLDivElement;
  let visible = false;
  let observer: IntersectionObserver;

  onMount(() => {
    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          visible = true;
          observer.disconnect();
        }
      },
      {
        root,
        rootMargin: '100px',
      },
    );

    observer.observe(el);
  });

  onDestroy(() => observer?.disconnect());
</script>

<div bind:this={el}>
  {#if visible}
    <slot />
  {/if}
</div>
