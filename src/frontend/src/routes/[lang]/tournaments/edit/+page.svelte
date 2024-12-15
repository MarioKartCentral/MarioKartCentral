<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { onMount } from 'svelte';
  import type { Tournament } from '$lib/types/tournament';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_tournament_permission, tournament_permissions, check_permission } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let tournament: Tournament;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    let tournament_id = param_id ? Number(param_id) : null;
    const res = await fetch(`/api/tournaments/${tournament_id}`);
    if (res.status === 200) {
      const body: Tournament = await res.json();
      tournament = body;
    }
  });
</script>

{#if tournament}
  {#if check_tournament_permission(user_info, tournament_permissions.edit_tournament, tournament.id, tournament.series_id)}
    <CreateEditTournamentForm tournament_id={tournament.id} data={tournament} 
    series_restrict={!check_permission(user_info, tournament_permissions.edit_tournament)} />
  {:else}
    {$LL.NO_PERMISSION()}
  {/if}
{/if}
