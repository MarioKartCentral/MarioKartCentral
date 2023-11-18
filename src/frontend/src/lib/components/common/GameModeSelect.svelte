<script lang="ts">
  import { valid_games, valid_modes, mode_names } from '$lib/util/util';
  import { createEventDispatcher } from 'svelte';

  export let game = 'mk8dx';
  export let mode = '150cc';

  const dispatch = createEventDispatcher();
</script>

<div class="option">
  <div>
    <label for="game">Game</label>
  </div>
  <div>
    <select
      name="game"
      bind:value={game}
      on:change={() => {
        [mode] = valid_modes[game];
        dispatch('change');
      }}
    >
      {#each Object.keys(valid_games) as game}
        <option value={game}>{valid_games[game]}</option>
      {/each}
    </select>
  </div>
</div>
<div class="option">
  <div>
    <label for="mode">Mode</label>
  </div>
  <div>
    <select name="mode" bind:value={mode} on:change={() => dispatch('change')}>
      {#each valid_modes[game] as mode}
        <option value={mode}>{mode_names[mode]}</option>
      {/each}
    </select>
  </div>
</div>

<style>
  .option {
    margin-bottom: 10px;
  }
</style>
