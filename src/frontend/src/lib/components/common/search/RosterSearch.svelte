<script lang="ts">
  import type { TeamList } from '$lib/types/team';
  import type { TeamRoster } from '$lib/types/team-roster';
  import LL from '$i18n/i18n-svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import Search from './Search.svelte';

  export let roster: TeamRoster | null = null;
  export let game: string | null = null;
  export let mode: string | null = null;
  export let isActive: boolean | null = null;
  export let isHistorical: boolean | null = null;
  export let showId: boolean = false;
  export let id: string = 'roster-search';
  export let ariaLabel: string | undefined = undefined;
  export let ariaLabelledby: string | undefined = undefined;

  let searchQuery: string;
  let timeout: number | null;
  let results: TeamRoster[] | undefined;
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

  $: url = (() => {
    const queryParams: string[] = [];
    if (searchQuery) queryParams.push(`name=${searchQuery}`);
    if (game) queryParams.push(`game=${game}`);
    if (mode) queryParams.push(`mode=${mode}`);
    if (isActive !== null) queryParams.push(`is_active=${isActive}`);
    if (isHistorical !== null) queryParams.push(`is_historical=${isHistorical}`);
    const queryString = queryParams.join('&');
    return `/api/registry/teams?${queryString}`;
  })();

  async function getResults() {
    const res = await fetch(url);
    if (res.ok) {
      const body: TeamList = await res.json();
      const { teams } = body;
      results = teams.flatMap((t) => t.rosters.filter((r) => (!game || r.game === game) && (!mode || r.mode === mode)));
    }
  }
</script>

<Search
  {id}
  placeholder={$LL.TEAMS.PROFILE.SEARCH_FOR_ROSTERS()}
  {ariaLabel}
  {ariaLabelledby}
  bind:searchQuery
  bind:selected={roster}
  bind:results
  bind:container
  oninput={handleSearch}
  optionLabel={(option) => `ID: ${option.id}, ${option.name} (${option.mode})`}
  let:option
>
  <div slot="selected" class="flex items-center gap-2" let:selected={roster}>
    {#if roster}
      <TagBadge tag={roster.tag} color={roster.color} />
      {roster.name}
    {/if}
  </div>
  {#if showId}
    <div class="w-[36px] whitespace-nowrap">
      {option.id}
    </div>
  {/if}
  <div>
    <TagBadge tag={option.tag} color={option.color} />
  </div>
  <div class="flex-1">
    {option.name}
  </div>
  <div>
    <GameBadge game={option.game} />
    <ModeBadge mode={option.mode} />
  </div>
</Search>
