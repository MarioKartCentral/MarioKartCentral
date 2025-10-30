<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import CancelButton from './buttons/CancelButton.svelte';

  const dispatch = createEventDispatcher<{ close: null }>();

  let dialog: HTMLDialogElement;
  export let header: string | null = null;

  export function open() {
    dialog.showModal();
  }

  export function close() {
    dialog.close();
    dispatch('close');
  }
</script>

<dialog bind:this={dialog}>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="outer" on:click={close}>
    <div class="container" on:click|stopPropagation>
      <div class="header bg-primary-800">
        <div>
          {#if header}
            <h3>{header}</h3>
          {/if}
        </div>
        <div class="exit">
          <CancelButton on:click={close} />
        </div>
      </div>
      <div class="content">
        <slot />
      </div>
    </div>
  </div>
</dialog>

<style>
  h3 {
    font-size: 18px;
    font-weight: 600;
  }
  dialog {
    position: fixed;
    width: 100%;
    height: 100%;
    background-color: transparent;
    color: white;
    border: none;
    outline: 0;
    margin: auto;
  }
  dialog::backdrop {
    background: rgba(0, 0, 0, 0.5);
    animation: fade-in 500ms;
  }
  .outer {
    width: 100%;
    height: 100%;
  }
  .container {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    min-height: 200px;
    transform: translate(-50%, -50%);
    background-color: rgba(64, 64, 64, 0.9);
  }
  @media (min-width: 600px) {
    .container {
      min-width: 400px;
      max-width: 700px;
    }
  }
  .header {
    display: grid;
    padding: 15px;
    min-height: 50px;
  }
  .content {
    padding: 15px;
    max-height: 500px;
    overflow-y: scroll;
  }
  .exit {
    position: absolute;
    right: 5%;
  }
</style>
