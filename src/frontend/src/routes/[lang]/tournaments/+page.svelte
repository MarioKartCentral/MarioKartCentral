<script lang="ts">
  import { onMount } from 'svelte';
  import TournamentPageItem from '$lib/components/tournaments/TournamentPageItem.svelte';
  import type { TournamentList } from '$lib/types/tournament-list';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import Section from '$lib/components/common/Section.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, series_permissions } from '$lib/util/permissions';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let totalTournaments = 0;
  let totalPages = 0;
  let currentPage = 1;

  let tournaments: TournamentListItem[] = [];

  async function fetchData() {
    let url = '/api/tournaments/list';
    url += '?page=' + currentPage;
    const res = await fetch(url);
    if (res.status === 200) {
      const body: TournamentList = await res.json();
      tournaments = body.tournaments;
      totalTournaments = body.tournament_count;
      totalPages = body.page_count;
    }
  }

  onMount(fetchData);
</script>

<Section header={$LL.NAVBAR.TOURNAMENTS()}>
  <div slot="header_content">
    {#if check_permission(user_info, series_permissions.create_tournament)}
      <Button href="/{$page.params.lang}/tournaments/create/select_template">Create Tournament</Button>
    {/if}
  </div>
  <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
  <div>
    {totalTournaments} Tournaments
  </div>
  {#key tournaments}
    {#each tournaments as tournament}
      <TournamentPageItem {tournament} />
    {/each}
  {/key}
  <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
</Section>
