<script lang="ts">
  import { country_codes } from '$lib/stores/country_codes';
  import LL from '$i18n/i18n-svelte';
  import type { PlayerFilter } from '$lib/types/registry/players/player-filter';
  import { valid_games } from '$lib/util/util';
  export let filters: PlayerFilter;
</script>
<select bind:value={filters.game}>
  <option value={null}>{$LL.PLAYER_LIST.FILTERS.ALL_GAMES()}</option>
  {#each Object.keys(valid_games) as game}
    <option value={game}>{valid_games[game]}</option>
  {/each}
</select>
<select bind:value={filters.country}>
  <option value={null}>{$LL.PLAYER_LIST.FILTERS.ALL_COUNTRIES()}</option>
  {#each country_codes as country_code}
    <option value={country_code}>{$LL.COUNTRIES[country_code]()}</option>
  {/each}
</select>
<input class="search" bind:value={filters.name_or_fc} type="text" placeholder={$LL.PLAYER_LIST.FILTERS.SEARCH_BY()} />

<style>
  .search {
    width: 300px;
  }
</style>
