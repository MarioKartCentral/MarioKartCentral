<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { BanFilter, BanHistoricalFilter } from '$lib/types/ban-filter';
  import type { BanListData } from '$lib/types/ban-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
  import ViewEditBan from '$lib/components/moderator/ViewEditBan.svelte';
  import BanListFilter from '$lib/components/moderator/BanListFilter.svelte';
  import BanList from '$lib/components/moderator/BanList.svelte';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  import { permissions } from '$lib/util/util';

  let player: PlayerInfo | null = null;
  let playerDetailed: PlayerInfo | null = null;
  let banFilter: BanFilter = {
    name: null,
    banned_by: null,
    is_indefinite: null,
    expires_before: null,
    expires_after: null,
    banned_before: null,
    banned_after: null,
    reason: null,
    page: null,
  };
  let banHistoricalFilter: BanHistoricalFilter = {
    name: null,
    banned_by: null,
    unbanned_by: null,
    unbanned_before: null,
    unbanned_after: null,
    is_indefinite: null,
    expires_before: null,
    expires_after: null,
    banned_before: null,
    banned_after: null,
    reason: null,
    page: null,
  };
  let banListData: BanListData = {
    ban_list: [],
    ban_count: 0,
    page_count: 1,
  };
  let historicalBanListData: BanListData = {
    ban_list: [],
    ban_count: 0,
    page_count: 1,
  };

  let currentBanPage: number = 1;
  let currentHistPage: number = 1;

  $: updatePlayerDetailed(player);

  async function updatePlayerDetailed(player: PlayerInfo | null) {
    if (!player) {
      playerDetailed = null;
      return;
    }

    const res = await fetch(`/api/registry/players/${player.id}`);
    if (res.status === 200) {
      playerDetailed = await res.json();
    }
  };

  function handleCancel() {
    player = null;
  };

  function getQueryString(filter: BanFilter | BanHistoricalFilter) {
    let params = [];
    let key: keyof (BanFilter | BanHistoricalFilter);
    for (key in filter) {
      if (filter[key] !== null)
        params.push(`${key}=${filter[key]}`);
    }
    return params.join("&");
  };

  async function updateBanList(isPageChange: boolean) {
    banFilter.page = isPageChange ? currentBanPage : 1;
    const res = await fetch(`/api/registry/players/bans?${getQueryString(banFilter)}`);
    if (res.status === 200) {
      banListData = await res.json();
    }
  };
  async function updateHistoricalBanList(isPageChange: boolean) {
    banHistoricalFilter.page = isPageChange ? currentHistPage : 1;
    const res = await fetch(`/api/registry/players/historicalBans?${getQueryString(banHistoricalFilter)}`);
    if (res.status === 200)
      historicalBanListData = await res.json();
  };

  onMount(async () => {
    updateBanList(false);
    updateHistoricalBanList(false);
  });
</script>

<svelte:head>
  <title>Player Bans | Mario Kart Central</title>
</svelte:head>

<PermissionCheck permission={permissions.ban_player}>
  <Section header={$LL.PLAYER_BAN.BAN_PLAYER()}>
    <PlayerSearch bind:player={player}/>
    {#if playerDetailed}
      {#if playerDetailed.ban_info}
        <strong>{$LL.PLAYER_BAN.THE_PLAYER_IS_ALREADY_BANNED()}</strong>
        <hr/>
        <ViewEditBan banInfo={playerDetailed.ban_info}/>
      {:else}
        <br/>
        <BanPlayerForm playerId={playerDetailed.id} playerName={playerDetailed.name} {handleCancel}/>
      {/if}
    {/if}
  </Section>

  <Section header={$LL.PLAYER_BAN.LIST_OF_BANNED_PLAYERS()}>
    <BanListFilter bind:filter={banFilter} handleSubmit={() => updateBanList(false)}/>
    <div class="player-count">
      <PageNavigation bind:currentPage={currentBanPage} bind:totalPages={banListData.page_count} refresh_function={() => updateBanList(true)}/>
      {banListData.ban_count} {banListData.ban_count === 1 ? $LL.PLAYER_BAN.PLAYER() : $LL.PLAYER_BAN.PLAYERS()}
    </div>
    <BanList banInfoDetailedArray={banListData.ban_list} />
  </Section>

  <Section header={$LL.PLAYER_BAN.LIST_OF_HISTORICAL_BANS()}>
    <BanListFilter bind:filter={banHistoricalFilter} handleSubmit={() => updateHistoricalBanList(false)}/>
    <div class="player-count">
      <PageNavigation bind:currentPage={currentHistPage} bind:totalPages={historicalBanListData.page_count} refresh_function={() => updateHistoricalBanList(true)}/>
      {historicalBanListData.ban_count} {historicalBanListData.ban_count === 1 ? $LL.PLAYER_BAN.PLAYER() : $LL.PLAYER_BAN.PLAYERS()}
    </div>
    <BanList banInfoDetailedArray={historicalBanListData.ban_list} isHistorical/>
  </Section>
</PermissionCheck>

<style>
  hr {
    margin: 10px 0px;
  }
  .player-count {
    margin-top: 10px;
  }
</style>