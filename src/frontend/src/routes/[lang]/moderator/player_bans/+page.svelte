<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { BanFilter, BanHistoricalFilter } from '$lib/types/ban-filter';
  import type { BanListData, BanInfoDetailed } from '$lib/types/ban-info';
  import type { UserInfo } from '$lib/types/user-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
  import ViewEditBan from '$lib/components/moderator/ViewEditBan.svelte';
  import BanListFilter from '$lib/components/moderator/BanListFilter.svelte';
  import BanListHistoricalFilter from '$lib/components/moderator/BanListHistoricalFilter.svelte';
  import BanList from '$lib/components/moderator/BanList.svelte';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  import { check_permission, permissions } from '$lib/util/permissions';
  import { user } from '$lib/stores/stores';

  let user_info: UserInfo;
  let player: PlayerInfo | null = null;
  let banInfo: BanInfoDetailed | null = null;
  let banFilter: BanFilter = {
    player_id: null,
    name: null,
    banned_by: null,
    is_indefinite: null,
    expires_before: null,
    expires_after: null,
    banned_before: null,
    banned_after: null,
    reason: null,
    comment: null,
    page: null,
  };
  let banHistoricalFilter: BanHistoricalFilter = {
    player_id: null,
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
    comment: null,
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

  user.subscribe((value) => {
    user_info = value;
  });

  let currentBanPage: number = 1;
  let currentHistPage: number = 1;

  $: updateBanInfo(player);

  async function updateBanInfo(player: PlayerInfo | null) {
    if (!player) {
      banInfo = null;
      return;
    }

    const res = await fetch(`/api/registry/players/bans?player_id=${player.id}`);
    if (res.status === 200) {
      const data: BanListData = await res.json();
      if (data.ban_count === 1)
        banInfo = data.ban_list[0];
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

{#if check_permission(user_info, permissions.ban_player)}
  <Section header={$LL.PLAYER_BAN.BAN_PLAYER()}>
    <PlayerSearch bind:player={player}/>
    {#if player}
      {#if banInfo}
        <strong>{$LL.PLAYER_BAN.THE_PLAYER_IS_ALREADY_BANNED()}</strong>
        <hr/>
        <ViewEditBan {banInfo}/>
      {:else}
        <br/>
        <BanPlayerForm playerId={player.id} playerName={player.name} {handleCancel}/>
      {/if}
    {/if}
  </Section>

  <Section header={$LL.PLAYER_BAN.LIST_OF_BANNED_PLAYERS()}>
    <BanListFilter bind:filter={banFilter} handleSubmit={() => updateBanList(false)}/>
    <div class="player-count">
      <PageNavigation bind:currentPage={currentBanPage} bind:totalPages={banListData.page_count} refresh_function={() => updateBanList(true)}/>
      {banListData.ban_count} {$LL.PLAYER_BAN.PLAYER(banListData.ban_count)}
    </div>
    <BanList banInfoDetailedArray={banListData.ban_list} />
  </Section>

  <Section header={$LL.PLAYER_BAN.LIST_OF_HISTORICAL_BANS()}>
    <BanListHistoricalFilter bind:filter={banHistoricalFilter} handleSubmit={() => updateHistoricalBanList(false)}/>
    <div class="player-count">
      <PageNavigation bind:currentPage={currentHistPage} bind:totalPages={historicalBanListData.page_count} refresh_function={() => updateHistoricalBanList(true)}/>
      {historicalBanListData.ban_count} {$LL.PLAYER_BAN.PLAYER(historicalBanListData.ban_count)}
    </div>
    <BanList banInfoDetailedArray={historicalBanListData.ban_list} isHistorical/>
  </Section>
{:else}
  You do not have permission to view this page.
{/if}
<style>
  hr {
    margin: 10px 0px;
  }
  .player-count {
    margin-top: 10px;
  }
</style>