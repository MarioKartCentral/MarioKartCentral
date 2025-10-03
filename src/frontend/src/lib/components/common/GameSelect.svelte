<script lang="ts">
  import { valid_games, valid_team_games } from '$lib/util/util';
  import LL from '$i18n/i18n-svelte';

  export let game: string | null = null;
  export let disabled = false;
  export let flex = false;
  export let required = false;
  export let all_option = false;
  export let hide_labels = false;
  export let is_team = false;
  export let disabled_games: string[] = [];

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const game_strings: any = $LL.GAMES;
</script>

<div class={flex ? 'flex' : ''}>
  {#if !hide_labels}
    <div>
      <label for="game">{$LL.COMMON.GAME()}</label>
    </div>
  {/if}
  <div>
    <select name="game" bind:value={game} on:change {disabled} {required}>
      {#if all_option}
        <option value={null} selected>{$LL.GAMES.ALL()}</option>
      {:else}
        <option value={null} disabled selected>{$LL.GAMES.SELECT()}</option>
      {/if}
      {#each is_team ? valid_team_games : valid_games as game}
        <option value={disabled_games.includes(game) ? null : game} disabled={disabled_games.includes(game)}>
          {game_strings[game.toUpperCase()]()}
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
