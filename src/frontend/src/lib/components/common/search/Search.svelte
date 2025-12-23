<script lang="ts" generics="T">
  import type { FormEventHandler } from 'svelte/elements';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import Table from '$lib/components/common/table/Table.svelte';
  import { clickOutside } from '$lib/actions/outclick.svelte';

  export let searchQuery: string | undefined;
  export let placeholder: string;
  export let oninput: FormEventHandler<HTMLInputElement>;
  export let results: T[];
  export let selected: T | null = null;
  export let container: HTMLDivElement;
  export let disabled: boolean = false;

  // addresses nested slot prop unknown type issue with svelte 4
  // https://github.com/sveltejs/language-tools/issues/1344
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface $$Slots {
    selected: {
      selected: T;
    };
    default: {
      result: T;
    };
  }

  let expanded: boolean = false;
  let inputElement: HTMLInputElement;

  function setOption(option: T | null) {
    expanded = false;
    selected = option;
  }

  function handleCancel() {
    setOption(null);
    setTimeout(() => inputElement.focus()); // required due to element visibility toggle
  }
</script>

<div class="container" use:clickOutside={expanded} on:outclick={() => (expanded = false)}>
  {#if selected}
    <div class="flex items-center gap-2">
      <slot name="selected" {selected} />
      {#if !disabled}
        <CancelButton on:click={handleCancel} />
      {/if}
    </div>
  {/if}
  <input
    class:hidden={selected}
    type="search"
    {placeholder}
    {disabled}
    aria-disabled={disabled}
    bind:this={inputElement}
    bind:value={searchQuery}
    on:input={oninput}
    on:focusin={() => (expanded = true)}
  />
  <div class="inner" bind:this={container}>
    {#key expanded}
      {#if expanded}
        <Table containerClass="rounded-none" data={results || []} let:item={result}>
          <tr
            role="option"
            tabindex="0"
            aria-selected={selected === result}
            on:click={() => setOption(result)}
            on:keydown={(event) => event.key === 'Enter' && setOption(result)}
          >
            <slot {result} />
          </tr>
        </Table>
      {/if}
    {/key}
  </div>
</div>

<style>
  .container {
    max-width: 400px;
    position: relative;
  }
  input {
    width: 100%;
  }

  div.inner {
    position: absolute;
    width: 100%;
    max-height: 300px;
    overflow-y: scroll;
    user-select: none;
    cursor: default;
    background-color: black;
    z-index: 1;
  }

  tr {
    transition: background-color 200ms ease-in-out;
    cursor: pointer;
    outline-offset: -4px; /* move outline inside to avoid being hidden due to scroll container */
  }

  tr:nth-child(2n) {
    background-color: rgba(255, 255, 255, 0.2);
  }

  tr:nth-child(2n + 1) {
    background-color: rgba(255, 255, 255, 0.18);
  }

  tr:hover,
  tr:focus-visible {
    background-color: rgba(255, 255, 255, 0.25);
  }
</style>
