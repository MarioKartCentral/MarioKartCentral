<script lang="ts">
  import { valid_games, valid_team_games } from '$lib/util/util';

  export let game: string | null = null;
  export let disabled = false;
  export let flex = false;
  export let required = false;
  export let all_option = false;
  export let hide_labels = false;
  export let is_team = false;
  export let disabled_games: string[] = [];
</script>

<div class={flex ? 'flex' : ''}>
  {#if !hide_labels}
    <div>
      <label for="game">Game</label>
    </div>
  {/if}
  <div>
    <select name="game" bind:value={game} on:change {disabled} {required}>
      {#if all_option}
        <option value={null} selected>All Games</option>
      {:else}
        <option value={null} disabled selected>Select a game...</option>
      {/if}
      {#each is_team ? Object.keys(valid_team_games) : Object.keys(valid_games) as game}
        <option value={disabled_games.includes(game) ? null : game} disabled={disabled_games.includes(game)}
          >{valid_games[game]}</option
        >
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

