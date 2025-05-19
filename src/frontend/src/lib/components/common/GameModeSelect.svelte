<script lang="ts">
  import { valid_modes, valid_team_modes } from '$lib/util/util';
  import { createEventDispatcher } from 'svelte';
  import GameSelect from './GameSelect.svelte';
  import LL from '$i18n/i18n-svelte';

  export let game: string | null = null;
  export let mode: string | null = null;
  export let disabled = false;
  export let flex = false;
  export let required = false;
  export let all_option = false;
  export let hide_labels = false;
  export let inline = false;
  export let is_team = false;

  const dispatch = createEventDispatcher();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mode_strings: any = $LL.MODES;
</script>

<div class={inline ? 'flex gap' : ''}>
  <div class="option {inline ? '' : 'margin'}">
    <GameSelect
      bind:game
      on:change={() => {
        if (game) {
          [mode] = valid_modes[game];
        } else {
          mode = null;
        }
        dispatch('change');
      }}
      {disabled}
      {flex}
      {required}
      {all_option}
      {hide_labels}
      {is_team}
    />
  </div>

  <div class="option {flex ? 'flex' : ''}">
    {#if !hide_labels}
      <div>
        <label for="mode">{$LL.COMMON.MODE()}</label>
      </div>
    {/if}
    <div>
      <select name="mode" bind:value={mode} on:change={() => dispatch('change')} {disabled} {required}>
        {#if all_option}
          <option value={null} selected>{$LL.MODES.ALL()}</option>
        {:else}
          <option value={null} disabled selected>{$LL.MODES.SELECT()}</option>
        {/if}
        {#if game}
          {#each is_team ? valid_team_modes[game] : valid_modes[game] as mode}
            <option value={mode}>{mode_strings[mode.toUpperCase()]()}</option>
          {/each}
        {/if}
      </select>
    </div>
  </div>
</div>

<style>
  .flex {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
  }
  select {
    width: 192px;
  }
  .gap {
    gap: 5px;
  }
  .margin {
    margin-bottom: 10px;
  }
</style>
