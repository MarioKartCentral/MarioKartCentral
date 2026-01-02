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

  let searchQuery: string;
  let timeout: number | null;
  let results: TeamRoster[];
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
      console.log(teams);
      results = teams.flatMap((t) => t.rosters.filter((r) => (!game || r.game === game) && (!mode || r.mode === mode)));
    }
  }
</script>

<Search
  placeholder={$LL.TEAMS.PROFILE.SEARCH_FOR_ROSTERS()}
  bind:searchQuery
  bind:selected={roster}
  bind:results
  bind:container
  oninput={handleSearch}
  let:result
>
  <div slot="selected" class="flex items-center gap-2" let:selected={roster}>
    {#if roster}
      <TagBadge tag={roster.tag} color={roster.color} />
      {roster.name}
    {/if}
  </div>
  {#if showId}
    <td>
      {result.id}
    </td>
  {/if}
  <td>
    <TagBadge tag={result.tag} color={result.color} />
  </td>
  <td>
    {result.name}
  </td>
  <td>
    <GameBadge game={result.game} />
    <ModeBadge mode={result.mode} />
  </td>
</Search>
