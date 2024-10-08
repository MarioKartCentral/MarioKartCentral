<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import TeamProfile from '$lib/components/registry/teams/TeamProfile.svelte';
  import TeamRoster from '$lib/components/registry/teams/TeamRoster.svelte';
  import Button from "$lib/components/common/buttons/Button.svelte";
  import { check_team_permission, team_permissions, check_permission, permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';

  let id = 0;
  let team: Team;
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
      return;
    }
    const body: Team = await res.json();
    team = body;
  });
</script>

<svelte:head>
  <title>{team_name} | Mario Kart Central</title>
</svelte:head>

{#if team}
  {#if check_permission(user_info, permissions.manage_teams)}
    <Section header={$LL.NAVBAR.MODERATOR()}>
      <div slot="header_content">
        <Button href="/{$page.params.lang}/registry/teams/mod/manage_rosters?id={id}"
          >{$LL.TEAM_PROFILE.MANAGE_ROSTERS()}</Button
        >
        <Button href="/{$page.params.lang}/registry/teams/mod/edit?id={id}"
          >{$LL.TEAM_PROFILE.EDIT_TEAM()}</Button
        >
      </div>
    </Section>
  {/if}
  <Section header={$LL.TEAM_PROFILE.TEAM_PROFILE()}>
    <div slot="header_content">
      {#if team.approval_status === 'approved' && !team.is_historical}
        {#if check_team_permission(user_info, team_permissions.manage_rosters, id)}
          <Button href="/{$page.params.lang}/registry/teams/manage_rosters?id={id}"
            >{$LL.TEAM_PROFILE.MANAGE_ROSTERS()}</Button
          >
        {/if}
        {#if check_team_permission(user_info, team_permissions.edit_team_info, id)}
          <Button href="/{$page.params.lang}/registry/teams/edit?id={id}">{$LL.TEAM_PROFILE.EDIT_TEAM()}</Button
          >
        {/if}
      {/if}
    </div>
    <TeamProfile {team} />
  </Section>
  <Section header={$LL.TEAM_PROFILE.ROSTERS()}>
    {#each team.rosters.filter((r) => r.approval_status === 'approved') as roster}
      <TeamRoster {roster} />
    {/each}
  </Section>
{/if}
