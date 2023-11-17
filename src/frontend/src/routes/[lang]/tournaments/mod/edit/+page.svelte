<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { permissions, addPermission } from '$lib/util/util';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import { onMount } from 'svelte';
  import type { Tournament } from '$lib/types/tournament';

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
  <PermissionCheck permission={permissions.edit_tournament}>
    <CreateEditTournamentForm tournament_id={tournament.id} data={tournament} />
  </PermissionCheck>
{/if}
