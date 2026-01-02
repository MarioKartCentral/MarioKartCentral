<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import { ArrowUpRightFromSquareOutline } from 'flowbite-svelte-icons';
  import Flag from '$lib/components/common/Flag.svelte';
  import LazyLoad from '$lib/components/media/LazyLoad.svelte';
  import Search from './Search.svelte';

  export let player: PlayerInfo | null = null;
  export let fcType: string | null = null;
  export let registrationId: number | null = null;
  export let isShadow: boolean | null = null;
  export let includeShadowPlayers: boolean = false;
  export let hasConnectedUser: boolean | null = null;
  export let isBanned: boolean | null = null;
  export let showId: boolean = false;
  export let showFriendCode: boolean = false;
  export let showProfileLink: boolean = false;

  let searchQuery: string;
  let timeout: number | null;
  let results: PlayerInfo[];
  let container: HTMLDivElement;

  async function handleSearch() {
    if (timeout) {
      clearTimeout(timeout);
    }
    if (!searchQuery) {
      results = [];
      return;
    }
    timeout = setTimeout(getResults, 300);
  }

  async function getResults() {
    const res = await fetch(url);
    if (res.ok) {
      const body = await res.json();
      results = body['player_list'];
    }
  }

  $: url = (() => {
    const queryParams = [];
    queryParams.push('detailed=true');
    queryParams.push('matching_fcs_only=true');
    queryParams.push(`include_shadow_players=${includeShadowPlayers}`);
    if (searchQuery) queryParams.push(`name_or_fc=${searchQuery}`);
    if (fcType) queryParams.push(`fc_type=${fcType}`);
    if (registrationId) queryParams.push(`registration_id=${registrationId}`);
    if (isShadow !== null) queryParams.push(`is_shadow=${isShadow}`);
    if (hasConnectedUser !== null) queryParams.push(`has_connected_user=${hasConnectedUser}`);
    if (isBanned !== null) queryParams.push(`is_banned=${isBanned}`);
    const queryString = queryParams.join('&');
    return `/api/registry/players?${queryString}`;
  })();
</script>

<Search
  placeholder={$LL.PLAYERS.LIST.SEARCH_BY()}
  bind:searchQuery
  bind:selected={player}
  bind:results
  let:result
  bind:container
  oninput={handleSearch}
>
  <div slot="selected" class="flex items-center gap-2" let:selected={player}>
    {#if player}
      <Flag country_code={player.country_code} />
      <div class="flex items-center justify-center gap-1">
        <span>{player.name}</span>
        {#if showProfileLink}
          <a href="/{$page.params.lang}/registry/players/profile?id={player.id}" target="_blank">
            <ArrowUpRightFromSquareOutline size="sm" />
          </a>
        {/if}
      </div>
    {/if}
  </div>
  {#if showId}
    <td class="w-[30px] whitespace-nowrap">
      {result.id}
    </td>
  {/if}
  <td class="w-[40px] h-[40px] !px-0">
    <LazyLoad root={container}>
      <Flag country_code={result.country_code} />
    </LazyLoad>
  </td>
  <td>
    <span>
      {result.name}
    </span>
  </td>
  {#if showFriendCode}
    <td class="hidden sm:table-cell">
      {#if result.friend_codes.length}
        {result.friend_codes[0].fc}
      {/if}
    </td>
  {/if}
  {#if showProfileLink}
    <td class="hidden sm:table-cell w-[40px]">
      <a
        on:click|stopPropagation
        on:keydown|stopPropagation
        href="/{$page.params.lang}/registry/players/profile?id={result.id}"
        target="_blank"
      >
        <ArrowUpRightFromSquareOutline size="md" ariaLabel="Player Profile" />
      </a>
    </td>
  {/if}
</Search>
