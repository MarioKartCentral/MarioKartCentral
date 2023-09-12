<script lang="ts">
  import { onMount } from 'svelte';
  let dropdown_open = false;
  export function toggleDropdown() {
    dropdown_open = !dropdown_open;
  }

  const clickOutside = (event: MouseEvent) => {
    if ((event?.target as HTMLElement).closest('.dropdown')) return;
    dropdown_open = false;
  };

  onMount(() => {
    window.addEventListener('click', clickOutside);
    return () => {
      window.removeEventListener('click', clickOutside);
    };
  });
</script>

{#if dropdown_open}
  <div class="dropdown">
    <div class="dropdown-container">
      <slot />
    </div>
  </div>
{/if}

<style>
  .dropdown {
    position: relative;
    
  }

  .dropdown-container {
    background-color: #5ce49a;
    position: absolute;
    width: max-content;
    right: 0;
    z-index: 100;
    color: white;
    box-shadow: 0 0 8px #141414;
  }
</style>
