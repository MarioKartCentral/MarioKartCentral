<script lang="ts">
  import { AccordionItem } from 'flowbite-svelte';

  export let open = true;
</script>

<AccordionItem
  {open}
  defaultClass="flex items-center justify-between w-full font-medium text-left"
  borderClass=""
  borderOpenClass=""
  borderBottomClass=""
>
  <span slot="header">
    <h3><slot name="header" /></h3>
  </span>
  <div slot="arrowup">
    <svg
      class="w-3 h-3 text-white"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 10 6"
    >
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5 5 1 1 5" />
    </svg>
  </div>
  <div slot="arrowdown">
    <svg
      class="w-3 h-3 text-white"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 10 6"
    >
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4" />
    </svg>
  </div>
  <slot />
</AccordionItem>

<style>
  span {
    font-size: 1.17em;
  }
</style>
