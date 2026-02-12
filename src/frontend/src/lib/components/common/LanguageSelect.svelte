<script lang="ts">
  import { valid_languages } from '$lib/util/util';
  import LL from '$i18n/i18n-svelte';

  export let language: string | null = null;
  export let flex = false;
  export let required = false;
  export let all_option = true;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const language_strings: any = $LL.LANGUAGES;
</script>

<div class={flex ? 'flex' : ''}>
  <div>
    <select name="language" bind:value={language} on:change {required}>
      {#if all_option}
        <option value={null} selected>{$LL.LANGUAGES.ALL()}</option>
      {/if}
      {#each valid_languages as valid_language, index (index)}
        <option value={valid_language.value}>
          {language_strings[valid_language.label]()}
        </option>
      {/each}
    </select>
  </div>
</div>

<style>
  select {
    width: 192px;
  }
  .flex {
    display: flex;
    align-items: center;
  }
</style>
