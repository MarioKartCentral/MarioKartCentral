<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import TeamProfile from '$lib/components/registry/teams/TeamProfile.svelte';
  import TeamRoster from '$lib/components/registry/teams/TeamRoster.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { check_team_permission, team_permissions, check_permission, permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import TeamTransferList from '$lib/components/registry/teams/TeamTransferList.svelte';
  import { sortFilterRosters } from '$lib/util/util';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import TeamTournamentHistory from '$lib/components/registry/teams/TeamTournamentHistory.svelte';

  let id = 0;
  let team: Team;
  let not_found = false;
  $: team_name = team ? team.name : 'Registry';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/registry/teams/${id}`);
    if (res.status != 200) {
      not_found = true;
      return;
    }
    const body: Team = await res.json();
    team = body;
  });

  let game: string | null = null;
  let mode: string | null = null;

  function filter_team_page_rosters(t: Team) {
    // if we can manage rosters for our team we should be able to see the ones with 0 players on the team profile page
    let show_zero_player_rosters = check_team_permission(user_info, team_permissions.manage_rosters, t.id);
    let filtered = sortFilterRosters(t.rosters, false, show_zero_player_rosters).filter(
      (r) => (!game || r.game === game) && (!mode || r.mode === mode) && r.is_active,
    );
    return filtered;
  }
</script>

<svelte:head>
  <title>{team_name} | MKCentral</title>
</svelte:head>

{#if team && user_info.is_checked}
  {#if team.approval_status === 'approved' || check_team_permission(user_info, team_permissions.edit_team_info, team.id)}
    {#if check_permission(user_info, permissions.manage_teams)}
      <Section header={$LL.NAVBAR.MODERATOR()}>
        <div slot="header_content">
          <Button href="/{$page.params.lang}/registry/teams/mod/manage_rosters?id={id}"
            >{$LL.TEAMS.PROFILE.MANAGE_ROSTERS()}</Button
          >
          <Button href="/{$page.params.lang}/registry/teams/mod/edit?id={id}">{$LL.TEAMS.PROFILE.EDIT_TEAM()}</Button>
          <Button href="/{$page.params.lang}/registry/teams/manage_roles?id={id}">{$LL.ROLES.MANAGE_ROLES()}</Button>
        </div>
      </Section>
    {/if}
    <Section header={$LL.TEAMS.PROFILE.TEAM_PROFILE()}>
      <div slot="header_content">
        {#if team.approval_status === 'approved' && !team.is_historical}
          {#if check_team_permission(user_info, team_permissions.manage_rosters, id)}
            <Button href="/{$page.params.lang}/registry/teams/manage_rosters?id={id}"
              >{$LL.TEAMS.PROFILE.MANAGE_ROSTERS()}</Button
            >
          {/if}
          {#if check_team_permission(user_info, team_permissions.edit_team_info, id)}
            <Button href="/{$page.params.lang}/registry/teams/edit?id={id}">{$LL.TEAMS.PROFILE.EDIT_TEAM()}</Button>
          {/if}
        {/if}
      </div>
      {#if team.approval_status === 'pending'}
        {$LL.TEAMS.PROFILE.PENDING_APPROVAL()}
      {/if}
      <TeamProfile {team} />
    </Section>
    <Section header={$LL.TEAMS.PROFILE.ROSTERS()}>
      <div class="filter">
        <GameModeSelect bind:game bind:mode is_team flex inline hide_labels all_option />
      </div>
      {#key game}
        {#key mode}
          {#each filter_team_page_rosters(team) as roster (roster.id)}
            <TeamRoster {roster} />
          {:else}
            {$LL.TEAMS.PROFILE.NO_ACTIVE_ROSTERS()}
          {/each}
        {/key}
      {/key}
    </Section>
    <TeamTournamentHistory {team} />
    <TeamTransferList {team} />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{:else if not_found}
  {$LL.TEAMS.PROFILE.TEAM_NOT_FOUND()}
{/if}

<style>
  .filter {
    margin-bottom: 10px;
  }
</style>
