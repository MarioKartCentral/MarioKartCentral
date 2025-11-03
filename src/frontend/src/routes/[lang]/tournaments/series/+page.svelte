<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { TournamentSeriesBasic } from '$lib/types/tournaments/series/tournament-series';
  import { check_permission, permissions } from '$lib/util/permissions';
  import { onMount } from 'svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import SeriesPageItem from '$lib/components/tournaments/series/SeriesPageItem.svelte';
  import LL from '$i18n/i18n-svelte';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let series: TournamentSeriesBasic[] = [];

  type SeriesFilter = {
    name: string;
    is_historical: boolean | null;
    game: string | null;
    mode: string | null;
  };

  let filter: SeriesFilter = {
    name: '',
    is_historical: false,
    game: null,
    mode: null,
  };

  async function fetchData() {
    let filter_strings = [];
    for (const [key, value] of Object.entries(filter)) {
      if (value !== null) {
        filter_strings.push(`${key}=${value}`);
      }
    }
    const filter_string = filter_strings.join('&');
    const res = await fetch(`/api/tournaments/series/list?${filter_string}`);
    if (res.status === 200) {
      const body: TournamentSeriesBasic[] = await res.json();
      series = body;
    }
  }

  onMount(fetchData);
</script>

<Section header={$LL.TOURNAMENTS.TOURNAMENT_SERIES()}>
  <div slot="header_content">
    {#if check_permission(user_info, permissions.create_series)}
      <Button href="/{$page.params.lang}/tournaments/series/create">{$LL.TOURNAMENTS.SERIES.CREATE()}</Button>
    {/if}
  </div>
  <form on:submit|preventDefault={fetchData}>
    <div class="options">
      <GameModeSelect bind:game={filter.game} bind:mode={filter.mode} flex inline hide_labels all_option />
      <select bind:value={filter.is_historical}>
        <option value={null}>{$LL.TOURNAMENTS.SERIES.ALL_SERIES()}</option>
        <option value={false}>{$LL.TOURNAMENTS.SERIES.ACTIVE_SERIES()}</option>
        <option value={true}>{$LL.TOURNAMENTS.SERIES.HISTORICAL_SERIES()}</option>
      </select>
      <input bind:value={filter.name} placeholder={$LL.TOURNAMENTS.SEARCH_SERIES()} />
      <Button type="submit">{$LL.COMMON.FILTER()}</Button>
    </div>
  </form>
</Section>

{#each series as s (s.id)}
  <SeriesPageItem series={s} />
{/each}

<style>
  .options {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 5px;
  }
</style>
