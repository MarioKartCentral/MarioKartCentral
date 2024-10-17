<script lang="ts">
  import { valid_modes, valid_team_modes, mode_names } from '$lib/util/util';
  import { createEventDispatcher } from 'svelte';
  import GameSelect from './GameSelect.svelte';

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
</script>

<div class={inline ? "flex gap" : ""}>
  <div class="option">
    <GameSelect bind:game={game} on:change={() => {
      if(game) {
        [mode] = valid_modes[game];
      }
      else {
        mode = null;
      }
      dispatch('change');
    }} {disabled} {flex} {required} {all_option} {hide_labels} {is_team}/>
  </div>
  
  <div class="option {flex ? 'flex' : ''}">
    {#if !hide_labels}
      <div>
        <label for="mode">Mode</label>
      </div>
    {/if}
    <div>
      <select name="mode" bind:value={mode} on:change={() => dispatch('change')} {disabled} {required}>
        {#if all_option}
          <option value={null} selected>All Modes</option>
        {:else}
          <option value={null} disabled selected>Select a mode...</option>
        {/if}
        {#if game}
          {#each is_team ? valid_team_modes[game] : valid_modes[game] as mode}
            <option value={mode}>{mode_names[mode]}</option>
          {/each}
        {/if}
        
      </select>
    </div>
  </div>
</div>


<style>
  .option {
    margin-bottom: 10px;
  }
  .flex {
    display: flex;
    align-items: center;
  }
  select {
    width: 200px;
    margin-right: 10px;
  }
  .gap {
    gap: 5px;
  }
</style>
