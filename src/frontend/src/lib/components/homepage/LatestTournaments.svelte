<script lang="ts">
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import { onMount } from 'svelte';
  import TournamentList from '../tournaments/TournamentList.svelte';
  import { page } from '$app/stores';
  import HomeTournamentPageItem from './HomeTournamentPageItem.svelte';
  import HomeSection from './HomeSection.svelte';
  import LL from '$i18n/i18n-svelte';

  export let style: string;
  let tournaments: TournamentListItem[] = [];

  async function fetchLatestTournaments() {
    let url = `/api/tournaments/list?is_viewable=true&is_public=true`;
    const res = await fetch(url);
    if (res.status === 200) {
      const body: TournamentList = await res.json();
      tournaments = body.tournaments.slice(0, 6);
    }
  }

  onMount(fetchLatestTournaments);
</script>

<HomeSection
  header={$LL.HOMEPAGE.LATEST_TOURNAMENTS()}
  linkText={$LL.HOMEPAGE.VIEW_ALL_TOURNAMENTS()}
  link="/{$page.params.lang}/tournaments"
  {style}
  wrapperClass="!px-0 !pt-0"
>
  <div>
    {#key tournaments}
      {#each tournaments as tournament (tournament.id)}
        <HomeTournamentPageItem {tournament} />
      {/each}
    {/key}
  </div>
</HomeSection>
