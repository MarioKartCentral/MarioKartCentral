<script lang="ts">
  import { getToastState } from '$lib/stores/toast.svelte';
  import { CloseOutline } from 'flowbite-svelte-icons';
  import { fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { styles } from './styles';
  import LL from '$i18n/i18n-svelte';

  const duration = 250;
  const toast = getToastState();
  const toastItems = toast.items;

  $: activeToastItems = $toastItems.filter((item) => !item.hidden);
</script>

<div class="toast">
  {#each activeToastItems as item (item.id)}
    <div
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      class="flex gap-3 w-full items-center toast-item"
      style="--accent: {styles[item.color].accent};"
      in:fly={{ y: -20, duration }}
      out:fly={{ x: 80, duration }}
      animate:flip={{ duration }}
    >
      <div class="icon inline-flex items-center justify-center shrink-0">
        <svelte:component this={styles[item.color].icon} ariaLabel="Notification icon" size="lg" />
      </div>
      <div class="w-full">
        {item.message}
        {#if item.redirect}
          <span class="ellipsis">{$LL.COMMON.REDIRECTING()}</span>
        {/if}
      </div>

      {#if item.redirect?.isCancellable}
        <button
          class="hover:text-gray-300 underline cursor-pointer"
          on:click={() => toast.set(item.id, { hidden: true, timeoutId: undefined })}
        >
          {$LL.COMMON.CANCEL()}
        </button>
      {/if}

      {#if !item.redirect}
        <button class="cancel shrink-0 h-8 w-8 cursor-pointer" on:click={() => toast.set(item.id, { hidden: true })}>
          <CloseOutline size="lg" class="w-full" ariaLabel="Dismiss notification icon" />
        </button>
      {/if}
    </div>
  {/each}
</div>

<style>
  .toast {
    position: fixed;
    top: 80px;
    right: 1rem;
    z-index: 700;
    width: clamp(min(100dvw - 2rem, 400px), 25dvw, 600px);
    max-height: calc(100dvh - 80px);
  }

  .toast-item {
    --accent: rgba(255, 255, 255, 0.15);
    background-color: rgb(40, 40, 40);
    padding: 1rem 1.25rem;
    margin-block: 0.25rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    position: relative;
  }

  .toast-item::before {
    position: absolute;
    width: 4px;
    height: 100%;
    border-radius: 4px 0 0 4px;
    background-color: var(--accent);
    content: '';
    left: 0;
  }

  .icon {
    border-radius: 4px;
    padding: 4px;
    background-color: var(--accent);
  }

  .ellipsis::after {
    content: '...';
  }

  button.cancel:hover,
  button.cancel:focus {
    border-radius: 4px;
    background-color: rgba(255, 255, 255, 0.15);
  }

  @media (max-width: 320px) {
    .icon {
      display: none;
    }
  }

  @media (max-width: 400px) {
    .toast {
      right: 0;
      padding-inline: 1rem;
      width: 100%;
    }

    .toast-item {
      padding-inline: 0.75rem;
    }
  }

  @media (max-width: 1100px) {
    .toast {
      top: 64px;
    }
  }
</style>
