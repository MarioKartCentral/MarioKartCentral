<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import TeamProfile from '$lib/components/registry/teams/TeamProfile.svelte';
  import TeamRoster from '$lib/components/registry/teams/TeamRoster.svelte';
  import { setTeamPerms, team_permissions, permissions } from '$lib/util/util';
  import LinkButton from '$lib/components/common/LinkButton.svelte';
  import TeamPermissionCheck from '$lib/components/common/TeamPermissionCheck.svelte';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';

  let id = 0;
  let team: Team;
  $: team_name = team ? team.name : 'Registry';

  setTeamPerms();

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
  <PermissionCheck permission={permissions.manage_teams}>
    <Section header="Moderator">
      <div slot="header_content">
        <LinkButton href="/{$page.params.lang}/registry/teams/mod/manage_rosters?id={id}">Manage Rosters</LinkButton>
        <LinkButton href="/{$page.params.lang}/registry/teams/mod/edit?id={id}">Edit Team</LinkButton>
      </div>
    </Section>
  </PermissionCheck>
  <Section header="Team Profile">
    <div slot="header_content">
      {#if team.approval_status === 'approved' && !team.is_historical}
        <TeamPermissionCheck team_id={id} permission={team_permissions.manage_roles}>
          <LinkButton href="/{$page.params.lang}/registry/teams/manage_rosters?id={id}">Manage Rosters</LinkButton>
        </TeamPermissionCheck>
        <TeamPermissionCheck team_id={id} permission={team_permissions.edit_team_info}>
          <LinkButton href="/{$page.params.lang}/registry/teams/edit?id={id}">Edit Team</LinkButton>
        </TeamPermissionCheck>
      {/if}
    </div>
    <TeamProfile {team} />
  </Section>
  <Section header="Rosters">
    {#each team.rosters.filter((r) => r.approval_status === 'approved') as roster}
      <TeamRoster {roster} />
    {/each}
  </Section>
{/if}
