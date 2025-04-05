<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { onMount } from 'svelte';
  import type { Tournament } from '$lib/types/tournament';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_tournament_permission, tournament_permissions, check_permission } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';
  import type { CreateTournament } from '$lib/types/tournaments/create/create-tournament';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let tournament: Tournament;
  let data: CreateTournament;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    let tournament_id = param_id ? Number(param_id) : null;
    const res = await fetch(`/api/tournaments/${tournament_id}`);
    if (res.status === 200) {
      const body: Tournament = await res.json();
      tournament = body;
      data = {...body, logo_file: null, remove_logo: false,};
    }
  });
</script>

{#if user_info.is_checked}
  {#if check_tournament_permission(user_info, tournament_permissions.edit_tournament, tournament.id, tournament.series_id)}
    {#if tournament && data}
        <CreateEditTournamentForm tournament_id={tournament.id} {data} 
        series_restrict={!check_permission(user_info, tournament_permissions.edit_tournament)} /> 
    {/if}
  {:else}
      {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
