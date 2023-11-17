<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { permissions, addPermission, series_permissions, setSeriesPerms } from '$lib/util/util';
  import SeriesPermissionCheck from '$lib/components/common/SeriesPermissionCheck.svelte';
  import { onMount } from 'svelte';
  import type { Tournament } from '$lib/types/tournament';

  setSeriesPerms();
  addPermission(permissions.edit_tournament);

  let param_id = $page.url.searchParams.get('id');
  let tournament_id = param_id ? Number(param_id) : null;

  let tournament: Tournament;

  onMount(async () => {
    const res = await fetch(`/api/tournaments/${tournament_id}`);
    if (res.status === 200) {
      const body: Tournament = await res.json();
      tournament = body;
    }
  });
</script>

{#if tournament}
  <SeriesPermissionCheck series_id={tournament.series_id} permission={series_permissions.edit_tournament}>
    <CreateEditTournamentForm tournament_id={tournament.id} data={tournament} series_restrict={true} />
  </SeriesPermissionCheck>
{/if}
