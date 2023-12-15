<script lang="ts">
  import { country_codes } from '$lib/stores/country_codes';
  import type { PlayerFilter } from '$lib/types/registry/players/player-filter';
  import { valid_games } from '$lib/util/util';
  export let filters: PlayerFilter;

  const list = [
    { value: '', label: 'Show All' },
    { value: 'mk8dx', label: 'Show with MK8DX FC' },
    { value: 'mkw', label: 'Show with MKW FC' },
    { value: 'mkt', label: 'Show with MKT FC' },
    { value: 'mk7', label: 'Show with 3DS FC' },
    { value: 'mk8', label: 'Show with NNID' },
  ];
</script>

<select bind:value={filters.game}>
  <option value={null}>All Games</option>
  {#each Object.keys(valid_games) as game}
    <option value={game}>{valid_games[game]} players</option>
  {/each}
</select>
<select bind:value={filters.country}>
  <option value={null}>All Countries</option>
  {#each country_codes as country_code}
    <option value={country_code}>{country_code}</option>
  {/each}
</select>
<input class="search" bind:value={filters.name_or_fc} type="text" placeholder="Search by Name or Friend Code..."/>

<style>
  .search {
    width: 300px;
  }
</style>
