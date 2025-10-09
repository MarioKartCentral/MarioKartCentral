<script lang="ts">
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import ImageInput from '$lib/components/common/ImageInput.svelte';

  export let file: string | null;
  export let logo_url: string | null = null;
  export let remove_logo = false;
</script>

{#if logo_url && !remove_logo}
  <div>
    <CancelButton on:click={() => (remove_logo = true)} />
  </div>
  <div>
    <img src={logo_url} alt="logo" />
  </div>
{/if}
{#if !logo_url || remove_logo}
  <div>
    <ImageInput bind:file name="logo" />
  </div>
{/if}

<style>
  img {
    max-width: 100px;
    max-height: 100px;
  }
</style>
