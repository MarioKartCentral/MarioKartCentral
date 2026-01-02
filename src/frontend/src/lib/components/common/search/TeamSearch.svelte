<script lang="ts">
  import type { Team, TeamList } from '$lib/types/team';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import { ArrowUpRightFromSquareOutline } from 'flowbite-svelte-icons';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Search from './Search.svelte';

  export let team: Team | null = null;
  export let game: string | null = null;
  export let isActive: boolean | null = null;
  export let isHistorical: boolean | null = null;

  let searchQuery: string;
  let timeout: number | null;
  let results: Team[];
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
      const body: TeamList = await res.json();
      results = body.teams;
    }
  }

  $: url = (() => {
    const queryParams = [];
    if (searchQuery) queryParams.push(`name=${searchQuery}`);
    if (game) queryParams.push(`game=${game}`);
    if (isActive !== null) queryParams.push(`is_active=${isActive}`);
    if (isHistorical !== null) queryParams.push(`is_historical=${isHistorical}`);
    const queryString = queryParams.join('&');
    return `/api/registry/teams?${queryString}`;
  })();
</script>

<Search
  placeholder={$LL.TEAMS.PROFILE.SEARCH_FOR_TEAMS()}
  bind:searchQuery
  bind:selected={team}
  bind:results
  bind:container
  oninput={handleSearch}
  let:result
>
  <div slot="selected" class="flex items-center gap-2" let:selected={team}>
    {#if team}
      <TagBadge tag={team.tag} color={team.color} />
      <div class="flex items-center justify-center gap-1">
        <span>{team.name}</span>
        <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}" target="_blank">
          <ArrowUpRightFromSquareOutline size="sm" />
        </a>
      </div>
    {/if}
  </div>
  <td>
    {result.id}
  </td>
  <td>
    <TagBadge tag={result.tag} color={result.color} />
  </td>
  <td>
    {result.name}
  </td>
  <td class="sm:table-cell w-[40px]">
    <a
      on:click|stopPropagation
      on:keydown|stopPropagation
      href="/{$page.params.lang}/registry/teams/profile?id={result.id}"
      target="_blank"
    >
      <ArrowUpRightFromSquareOutline size="md" />
    </a>
  </td>
</Search>
