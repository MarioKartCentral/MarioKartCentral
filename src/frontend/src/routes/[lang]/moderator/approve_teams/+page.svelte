<script lang="ts">
  import { onMount } from 'svelte';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import type { Team, TeamList } from '$lib/types/team';
  import type { TeamRoster } from '$lib/types/team-roster';
  import { check_permission, permissions } from '$lib/util/permissions';
  import { locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import ConfirmButton from '$lib/components/common/buttons/ConfirmButton.svelte';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import LL from '$i18n/i18n-svelte';

  let rosters: TeamRoster[] = [];

  let pending_teams: Team[] = [];
  let denied_teams: Team[] = [];
  $: pending_rosters = rosters.filter((r) => r.approval_status === 'pending');
  $: denied_rosters = rosters.filter((r) => r.approval_status === 'denied');

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    const res = await fetch(`/api/registry/teams/pendingTeams`);
    if (res.status === 200) {
      const body: TeamList = await res.json();
      pending_teams = body.teams;
    }

    const res2 = await fetch(`/api/registry/teams/unapprovedRosters`);
    if (res2.status === 200) {
      const body: TeamRoster[] = await res2.json();
      rosters = body;
    }

    const res3 = await fetch(`/api/registry/teams/deniedTeams`);
    if(res3.status === 200) {
      const body: TeamList = await res3.json();
      denied_teams = body.teams;
    }
  });

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };

  async function approveTeam(team: Team) {
    let conf = window.confirm($LL.MODERATOR.APPROVE_TEAM_CONFIRM());
    if(!conf) {
      return;
    }
    const res = await fetch(`/api/registry/teams/${team.id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.APPROVE_TEAM_FAILED()}: ${result['title']}`);
    }
  }

  async function denyTeam(team: Team) {
    let conf = window.confirm($LL.MODERATOR.DENY_TEAM_CONFIRM());
    if(!conf) {
      return;
    }
    const res = await fetch(`/api/registry/teams/${team.id}/deny`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.DENY_TEAM_FAILED()}: ${result['title']}`);
    }
  }

  async function approveRoster(roster: TeamRoster) {
    let conf = window.confirm($LL.MODERATOR.APPROVE_ROSTER_CONFIRM());
    if(!conf) {
      return;
    }
    const res = await fetch(`/api/registry/teams/${roster.team_id}/approveRoster/${roster.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.APPROVE_ROSTER_FAILED()}: ${result['title']}`);
    }
  }

  async function denyRoster(roster: TeamRoster) {
    let conf = window.confirm($LL.MODERATOR.DENY_ROSTER_CONFIRM());
    if(!conf) {
      return;
    }
    const res = await fetch(`/api/registry/teams/${roster.team_id}/denyRoster/${roster.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.DENY_ROSTER_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if check_permission(user_info, permissions.manage_teams)}
  <Section header={$LL.MODERATOR.PENDING_TEAMS()}>
    {#if pending_teams.length}
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="game-mode"/>
      <col class="date mobile-hide" />
      <col class="approve" />
      <thead>
        <tr>
          <th>{$LL.COMMON.TAG()}</th>
          <th>{$LL.COMMON.NAME()}</th>
          <th>{$LL.COMMON.GAME_MODE()}</th>
          <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
          <th>{$LL.MODERATOR.APPROVE()}</th>
        </tr>
      </thead>
      <tbody>
        {#each pending_teams as team, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">
              <TagBadge tag={team.tag} color={team.color}/>
            </a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a></td>
            <td>
              <GameBadge game={team.rosters[0].game}/>
              <ModeBadge mode={team.rosters[0].mode}/>
            </td>
            <td class="mobile-hide">{new Date(team.creation_date * 1000).toLocaleString($locale, options)}</td>
            <td>
              <ConfirmButton on:click={() => approveTeam(team)}/>
              <CancelButton on:click={() => denyTeam(team)}/>
            </td>
          </tr>
        {/each}
      </tbody>
    </Table>
    {:else}
      {$LL.MODERATOR.NO_PENDING_TEAMS()}
    {/if}
    
  </Section>
  <Section header={$LL.MODERATOR.PENDING_ROSTERS()}>
    {#if pending_rosters.length}
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="game-mode"/>
      <col class="date mobile-hide" />
      <col class="approve" />
      <thead>
        <tr>
          <th>{$LL.COMMON.TAG()}</th>
          <th>{$LL.COMMON.NAME()}</th>
          <th>{$LL.COMMON.GAME_MODE()}</th>
          <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
          <th>{$LL.MODERATOR.APPROVE()}</th>
        </tr>
      </thead>
      <tbody>
        {#each pending_rosters as roster, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">
              <TagBadge tag={roster.tag} color={roster.color}/>
            </a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.name}</a></td>
            <td>
              <GameBadge game={roster.game}/>
              <ModeBadge mode={roster.mode}/>
            </td>
            <td class="mobile-hide">{new Date(roster.creation_date * 1000).toLocaleString($locale, options)}</td>
            <td>
              <ConfirmButton on:click={() => approveRoster(roster)}/>
              <CancelButton on:click={() => denyRoster(roster)}/>
            </td>
          </tr>
        {/each}
      </tbody>
    </Table>
    {:else}
      {$LL.MODERATOR.NO_PENDING_ROSTERS()}
    {/if}
    
  </Section>
  <Section header={$LL.MODERATOR.DENIED_TEAMS()}>
    {#if denied_teams.length}
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="game-mode"/>
      <col class="date mobile-hide" />
      <thead>
        <tr>
          <th>{$LL.COMMON.TAG()}</th>
          <th>{$LL.COMMON.NAME()}</th>
          <th>{$LL.COMMON.GAME_MODE()}</th>
          <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
        </tr>
      </thead>
      <tbody>
        {#each denied_teams as team, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">
              <TagBadge tag={team.tag} color={team.color}/>
            </a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a></td>
            <td>
              <GameBadge game={team.rosters[0].game}/>
              <ModeBadge mode={team.rosters[0].mode}/>
            </td>
            <td class="mobile-hide">{new Date(team.creation_date * 1000).toLocaleString($locale, options)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
    {:else}
      {$LL.MODERATOR.NO_DENIED_TEAMS()}
    {/if}
    
  </Section>
  <Section header={$LL.MODERATOR.DENIED_ROSTERS()}>
    {#if denied_rosters.length}
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="game-mode"/>
      <col class="date mobile-hide" />
      <thead>
        <tr>
          <th>{$LL.COMMON.TAG()}</th>
          <th>{$LL.COMMON.NAME()}</th>
          <th>{$LL.COMMON.GAME_MODE()}</th>
          <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
        </tr>
      </thead>
      <tbody>
        {#each denied_rosters as roster, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">
              <TagBadge tag={roster.tag} color={roster.color}/>
            </a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.name}</a></td>
            <td>
              <GameBadge game={roster.game}/>
              <ModeBadge mode={roster.mode}/>
            </td>
            <td class="mobile-hide">{new Date(roster.creation_date * 1000).toLocaleString($locale, options)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
    {:else}
      {$LL.MODERATOR.NO_DENIED_ROSTERS()}
    {/if}
    
  </Section>
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}

<style>
  col.tag {
    width: 10%;
  }
  col.name {
    width: 25%;
  }
  col.game-mode {
    width: 25%;
  }
  col.date {
    width: 15%;
  }
  col.approve {
    width: 25%;
  }
</style>
