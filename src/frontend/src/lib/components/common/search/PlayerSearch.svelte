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
  export let id: string = 'player-search';
  export let ariaLabel: string | undefined = undefined;
  export let ariaLabelledby: string | undefined = undefined;

  let searchQuery: string;
  let timeout: number | null;
  let results: PlayerInfo[] | undefined;
  let container: HTMLUListElement;

  async function handleSearch() {
    if (timeout) {
      clearTimeout(timeout);
    }
    if (!searchQuery) {
      results = undefined;
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
  {id}
  placeholder={$LL.PLAYERS.LIST.SEARCH_BY()}
  bind:searchQuery
  bind:selected={player}
  bind:results
  bind:container
  oninput={handleSearch}
  optionLabel={(option) => `ID: ${option.id}, ${option.name}`}
  {ariaLabel}
  {ariaLabelledby}
  let:option
>
  <div slot="selected" class="flex items-center gap-2" let:selected={player}>
    {#if player}
      <Flag country_code={player.country_code} />
      <div class="flex items-center justify-center gap-1">
        <span>
          {player.name}
        </span>
        {#if showProfileLink}
          <a href="/{$page.params.lang}/registry/players/profile?id={player.id}" target="_blank">
            <ArrowUpRightFromSquareOutline size="sm" ariaLabel="Player Profile" />
          </a>
        {/if}
      </div>
    {/if}
  </div>
  {#if showId}
    <div class="w-[45px] whitespace-nowrap">
      {option.id}
    </div>
  {/if}
  <div class="w-[40px] !px-0">
    <LazyLoad root={container}>
      <Flag country_code={option.country_code} />
    </LazyLoad>
  </div>
  <div class="flex-1">
    <span>
      {option.name}
    </span>
  </div>
  {#if showFriendCode}
    <div class="hidden sm:block">
      {#if option.friend_codes.length}
        {option.friend_codes[0].fc}
      {/if}
    </div>
  {/if}
  {#if showProfileLink}
    <div class="hidden sm:block ml-4">
      <a
        on:click|stopPropagation
        on:keydown|stopPropagation
        href="/{$page.params.lang}/registry/players/profile?id={option.id}"
        target="_blank"
        tabindex="-1"
      >
        <ArrowUpRightFromSquareOutline size="md" ariaLabel="Player Profile" aria-hidden="true" tabindex="-1" />
      </a>
    </div>
  {/if}
</Search>
