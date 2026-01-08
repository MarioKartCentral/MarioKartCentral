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
  export let id: string = 'team-search';
  export let ariaLabel: string | undefined = undefined;
  export let ariaLabelledby: string | undefined = undefined;

  let searchQuery: string;
  let timeout: number | null;
  let results: Team[] | undefined;
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
  {id}
  {ariaLabel}
  {ariaLabelledby}
  placeholder={$LL.TEAMS.PROFILE.SEARCH_FOR_TEAMS()}
  bind:searchQuery
  bind:selected={team}
  bind:results
  bind:container
  oninput={handleSearch}
  optionLabel={(option) => `ID: ${option.id}, ${option.name}`}
  let:option
>
  <div slot="selected" class="flex items-center gap-2" let:selected={team}>
    {#if team}
      <TagBadge tag={team.tag} color={team.color} />
      <div class="flex items-center justify-center gap-1">
        <span>{team.name}</span>
        <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}" target="_blank">
          <ArrowUpRightFromSquareOutline size="sm" ariaLabel="Team Profile" />
        </a>
      </div>
    {/if}
  </div>
  <div class="w-[36px] whitespace-nowrap">
    {option.id}
  </div>
  <div>
    <TagBadge tag={option.tag} color={option.color} />
  </div>
  <div class="flex-1">
    {option.name}
  </div>
  <div class="sm:block w-[40px] ml-4">
    <a
      on:click|stopPropagation
      on:keydown|stopPropagation
      href="/{$page.params.lang}/registry/teams/profile?id={option.id}"
      target="_blank"
      tabindex="-1"
    >
      <ArrowUpRightFromSquareOutline size="md" ariaLabel="Team Profile" aria-hidden="true" tabindex="-1" />
    </a>
  </div>
</Search>
