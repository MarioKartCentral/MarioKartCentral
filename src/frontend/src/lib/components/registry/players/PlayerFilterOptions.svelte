<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import type { PlayerFilter } from '$lib/types/registry/players/player-filter';
  import CountrySelect from '$lib/components/common/CountrySelect.svelte';
  import GameSelect from '$lib/components/common/GameSelect.svelte';
  export let filters: PlayerFilter;

</script>

<div class="flex">
  <GameSelect all_option hide_labels/>
  <CountrySelect bind:value={filters.country} is_filter={true}/>
  <input class="search" bind:value={filters.name_or_fc} type="text" placeholder={$LL.PLAYER_LIST.FILTERS.SEARCH_BY()} />
</div>


<style>
  .flex {
    display: flex;
    align-items: center;
  }
  .search {
    width: 300px;
  }
</style>
