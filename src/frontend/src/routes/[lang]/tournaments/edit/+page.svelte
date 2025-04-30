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
      data = {
        name: tournament.name,
        series_id: tournament.series_id,
        date_start: tournament.date_start,
        date_end: tournament.date_end,
        logo: tournament.logo,
        use_series_logo: tournament.use_series_logo,
        url: tournament.url,
        organizer: tournament.organizer,
        location: tournament.location,
        game: tournament.game,
        mode: tournament.mode,
        is_squad: tournament.is_squad,
        min_squad_size: tournament.min_squad_size,
        max_squad_size: tournament.max_squad_size,
        squad_name_required: tournament.squad_name_required,
        squad_tag_required: tournament.squad_tag_required,
        teams_allowed: tournament.teams_allowed,
        teams_only: tournament.teams_only,
        team_members_only: tournament.team_members_only,
        min_representatives: tournament.min_representatives,
        host_status_required: tournament.host_status_required,
        mii_name_required: tournament.mii_name_required,
        require_single_fc: tournament.require_single_fc,
        checkins_enabled: tournament.checkins_enabled,
        checkins_open: tournament.checkins_open,
        min_players_checkin: tournament.min_players_checkin,
        verification_required: tournament.verification_required,
        description: tournament.description,
        use_series_description: tournament.use_series_description,
        ruleset: tournament.ruleset,
        use_series_ruleset: tournament.use_series_ruleset,
        registrations_open: tournament.registrations_open,
        registration_deadline: tournament.registration_deadline,
        registration_cap: tournament.registration_cap,
        is_viewable: tournament.is_viewable,
        is_public: tournament.is_public,
        is_deleted: tournament.is_deleted,
        show_on_profiles: tournament.show_on_profiles,
        series_stats_include: tournament.series_stats_include,
        verified_fc_required: tournament.verified_fc_required,
        bagger_clause_enabled: tournament.bagger_clause_enabled,
        logo_file: null,
        remove_logo: false,
      };
    }
  });
</script>

{#if user_info.is_checked && tournament && data}
  {#if check_tournament_permission(user_info, tournament_permissions.edit_tournament, tournament.id, tournament.series_id)}
      <CreateEditTournamentForm tournament_id={tournament.id} {data} 
      series_restrict={!check_permission(user_info, tournament_permissions.edit_tournament)} /> 
  {:else}
      {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
