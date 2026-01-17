<script lang="ts" generics="T extends { id: number }">
  import { tick } from 'svelte';
  import type { FormEventHandler } from 'svelte/elements';
  import LL from '$i18n/i18n-svelte';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import { clickOutside } from '$lib/actions/outclick.svelte';

  export let searchQuery: string | undefined;
  export let placeholder: string;
  export let oninput: FormEventHandler<HTMLInputElement>;
  export let results: T[] | undefined;
  export let selected: T | null = null;
  export let container: HTMLUListElement;
  export let disabled: boolean = false;
  export let id: string;
  export let optionLabel: (option: T) => string;
  export let ariaLabel: string | undefined = undefined;
  export let ariaLabelledby: string | undefined = undefined;

  // addresses nested slot prop unknown type issue with svelte 4
  // https://github.com/sveltejs/language-tools/issues/1344
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface $$Slots {
    selected: {
      selected: T;
    };
    default: {
      option: T;
    };
  }
  let searchFocussed: boolean = false;
  let popupExpanded: boolean = false;
  $: ariaExpanded = popupExpanded && results && results.length > 0 ? true : false;
  let inputElement: HTMLInputElement;
  let cancelContainer: HTMLDivElement;
  let activeDescendant: string | undefined;

  const getOptionId = (option: T) => `${id}-option-${option.id}`;

  function setOption(option: T | null) {
    handleOutclick();
    selected = option;
    activeDescendant = undefined;
  }

  function handleCancel() {
    setOption(null);
    setTimeout(() => inputElement.focus()); // required due to element visibility toggle
  }

  function handleOutclick() {
    searchFocussed = false;
    popupExpanded = false;
  }

  function handleClick() {
    handleFocusin();
  }

  function handleFocusin() {
    if (searchFocussed && popupExpanded) return;
    if (results) {
      popupExpanded = true;
    }
    searchFocussed = true;
  }

  function handleBlur() {
    activeDescendant = undefined;
  }

  // display popup on any update to results (if query is not empty)
  $: {
    if (searchFocussed && results) {
      popupExpanded = true;
    }
  }

  $: activeElement =
    container && activeDescendant ? (container.querySelector(`#${activeDescendant}`) as HTMLButtonElement) : null;

  async function handleKeyDown(event: KeyboardEvent) {
    if (!results) return;
    const idx = activeDescendant ? results.findIndex((row) => getOptionId(row) === activeDescendant) : -1;
    switch (event.key) {
      case 'ArrowDown':
        if (results.length) {
          popupExpanded = true;
          event.preventDefault();
          activeDescendant = getOptionId(results[(idx + 1) % results.length]);
        }
        return;
      case 'ArrowUp':
        if (results.length) {
          popupExpanded = true;
          event.preventDefault();
          activeDescendant = getOptionId(results[(idx <= 0 ? results.length : idx) - 1]);
        }
        return;
      case 'ArrowLeft':
      case 'ArrowRight':
        activeDescendant = undefined;
        return;
      case 'Home':
        if (results.length) {
          event.preventDefault();
          activeDescendant = getOptionId(results[0]);
        }
        return;
      case 'End':
        if (results.length) {
          event.preventDefault();
          activeDescendant = getOptionId(results[results.length - 1]);
        }
        return;
      case 'Escape':
        if (popupExpanded) {
          event.preventDefault();
          popupExpanded = false;
          activeDescendant = undefined;
        } else {
          searchQuery = undefined;
        }
        return;
      case 'Enter':
        if (activeDescendant) {
          event.preventDefault();
          activeElement?.click();
          await tick();
          cancelContainer.querySelector('button')?.focus();
        }
        return;
      case 'Tab':
        handleOutclick();
    }
  }

  // remove or reposition outline on updates to the search
  $: {
    if (!results) {
      activeDescendant = undefined;
      popupExpanded = false;
    } else if (activeDescendant && !results.some((result) => getOptionId(result) === activeDescendant)) {
      activeDescendant = results.length ? getOptionId(results[0]) : undefined;
    }
  }

  function scrollActiveElement(container: HTMLElement, active: HTMLElement) {
    const containerRect = container.getBoundingClientRect();
    const activeRect = active.getBoundingClientRect();

    if (activeRect.top < containerRect.top) {
      container.scrollTop -= containerRect.top - activeRect.top;
    }

    if (activeRect.bottom > containerRect.bottom) {
      container.scrollTop += activeRect.bottom - containerRect.bottom;
    }
  }

  $: {
    if (popupExpanded && activeElement) {
      scrollActiveElement(container, activeElement);
    }
  }
</script>

<div class="container" use:clickOutside={searchFocussed} on:outclick={handleOutclick}>
  {#if selected}
    <div class="flex items-center gap-2" bind:this={cancelContainer}>
      <slot name="selected" {selected} />
      {#if !disabled}
        <CancelButton on:click={handleCancel} ariaLabel="Return to search. Selected option: {optionLabel(selected)}" />
      {/if}
    </div>
  {/if}

  <input
    {id}
    type="text"
    role="combobox"
    class:hidden={selected}
    {placeholder}
    {disabled}
    aria-expanded={ariaExpanded}
    aria-controls="{id}-results"
    aria-autocomplete="list"
    aria-activedescendant={activeDescendant}
    aria-disabled={disabled}
    aria-label={ariaLabel}
    aria-labelledby={ariaLabelledby}
    aria-haspopup="listbox"
    bind:this={inputElement}
    bind:value={searchQuery}
    on:focusin={handleFocusin}
    on:input={oninput}
    on:keydown={handleKeyDown}
    on:click={handleClick}
    on:blur={handleBlur}
  />
  <ul class="inner" bind:this={container} id="{id}-results" role="listbox" class:hidden={!popupExpanded}>
    {#if results && results.length === 0}
      <div class="item text-center not-sr-only">
        {$LL.COMMON.RESULTS({ count: 0 })}
      </div>
    {/if}

    {#each results || [] as option (option.id)}
      {@const optionId = getOptionId(option)}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <li
        role="option"
        class="item flex gap-2 items-center w-full"
        id={optionId}
        aria-label={optionLabel(option)}
        aria-selected={optionId === activeDescendant}
        on:click={() => setOption(option)}
      >
        <slot {option} />
      </li>
    {/each}
  </ul>
</div>

<style>
  .container {
    max-width: 400px;
    position: relative;
  }
  input {
    width: 100%;
  }

  ul.inner {
    position: absolute;
    width: 100%;
    max-height: 300px;
    overflow-y: scroll;
    user-select: none;
    cursor: default;
    background-color: black;
    z-index: 1;
  }

  .item {
    font-size: small;
    padding: 10px;
    background-color: rgba(255, 255, 255, 0.18);
  }

  .item:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .item[role='option']:nth-child(2n + 1) {
    background-color: rgba(255, 255, 255, 0.2);
  }

  .item[role='option'] {
    transition: background-color 200ms ease-in-out;
    cursor: pointer;
    outline-offset: -4px; /* move outline inside to avoid being hidden due to scroll container */
  }

  .item[role='option']:hover,
  .item[role='option']:focus-visible,
  .item[role='option'][aria-selected='true'] {
    background-color: rgba(255, 255, 255, 0.25);
  }

  .item[role='option'][aria-selected='true'] {
    outline: auto;
  }
</style>
