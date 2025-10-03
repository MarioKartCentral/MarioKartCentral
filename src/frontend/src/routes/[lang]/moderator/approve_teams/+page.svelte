<script lang="ts">
  import { onMount } from 'svelte';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import type { Team, TeamList } from '$lib/types/team';
  import type { TeamRoster } from '$lib/types/team-roster';
  import type { RosterList } from '$lib/types/roster-list';
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
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';

  let pending_teams: Team[] = [];
  let pending_rosters: TeamRoster[] = [];

  let denied_team_page = 1;
  let denied_team_total_pages = 1;
  let denied_teams: Team[] = [];

  let denied_roster_page = 1;
  let denied_roster_total_pages = 1;
  let denied_rosters: TeamRoster[] = [];

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  async function getPendingTeams() {
    const res = await fetch(`/api/registry/teams/pendingTeams`);
    if (res.status === 200) {
      const body: TeamList = await res.json();
      pending_teams = body.teams;
    }
  }

  async function getDeniedTeams() {
    const res = await fetch(`/api/registry/teams/deniedTeams?page=${denied_team_page}`);
    if (res.status === 200) {
      const body: TeamList = await res.json();
      denied_teams = body.teams;
      denied_team_total_pages = body.page_count;
    }
  }

  async function getPendingRosters() {
    const res = await fetch(`/api/registry/teams/listRosters?approval_status=pending`);
    if (res.status === 200) {
      const body: RosterList = await res.json();
      pending_rosters = body.rosters;
    }
  }

  async function getDeniedRosters() {
    const res = await fetch(`/api/registry/teams/listRosters?approval_status=denied&page=${denied_roster_page}`);
    if (res.status === 200) {
      const body: RosterList = await res.json();
      denied_rosters = body.rosters;
      denied_roster_total_pages = body.page_count;
    }
  }

  onMount(async () => {
    await getPendingTeams();
    await getPendingRosters();
    await getDeniedTeams();
    await getDeniedRosters();
  });

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };

  async function approveTeam(team: Team) {
    let conf = window.confirm($LL.MODERATOR.APPROVE_TEAM_CONFIRM());
    if (!conf) {
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
    if (!conf) {
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
    if (!conf) {
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
    if (!conf) {
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
        <col class="game-mode" />
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
              <td
                ><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">
                  <TagBadge tag={team.tag} color={team.color} />
                </a></td
              >
              <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a></td>
              <td>
                <GameBadge game={team.rosters[0].game} />
                <ModeBadge mode={team.rosters[0].mode} />
              </td>
              <td class="mobile-hide">{new Date(team.creation_date * 1000).toLocaleString($locale, options)}</td>
              <td>
                <ConfirmButton on:click={() => approveTeam(team)} />
                <CancelButton on:click={() => denyTeam(team)} />
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
        <col class="game-mode" />
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
              <td
                ><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">
                  <TagBadge tag={roster.tag} color={roster.color} />
                </a></td
              >
              <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.name}</a></td>
              <td>
                <GameBadge game={roster.game} />
                <ModeBadge mode={roster.mode} />
              </td>
              <td class="mobile-hide">{new Date(roster.creation_date * 1000).toLocaleString($locale, options)}</td>
              <td>
                <ConfirmButton on:click={() => approveRoster(roster)} />
                <CancelButton on:click={() => denyRoster(roster)} />
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
      <PageNavigation
        bind:currentPage={denied_team_page}
        bind:totalPages={denied_team_total_pages}
        refresh_function={getDeniedTeams}
      />
      <Table>
        <col class="tag" />
        <col class="name" />
        <col class="game-mode" />
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
              <td
                ><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">
                  <TagBadge tag={team.tag} color={team.color} />
                </a></td
              >
              <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a></td>
              <td>
                <GameBadge game={team.rosters[0].game} />
                <ModeBadge mode={team.rosters[0].mode} />
              </td>
              <td class="mobile-hide">{new Date(team.creation_date * 1000).toLocaleString($locale, options)}</td>
            </tr>
          {/each}
        </tbody>
      </Table>
      <PageNavigation
        bind:currentPage={denied_team_page}
        bind:totalPages={denied_team_total_pages}
        refresh_function={getDeniedTeams}
      />
    {:else}
      {$LL.MODERATOR.NO_DENIED_TEAMS()}
    {/if}
  </Section>
  <Section header={$LL.MODERATOR.DENIED_ROSTERS()}>
    {#if denied_rosters.length}
      <PageNavigation
        bind:currentPage={denied_roster_page}
        bind:totalPages={denied_roster_total_pages}
        refresh_function={getDeniedRosters}
      />
      <Table>
        <col class="tag" />
        <col class="name" />
        <col class="game-mode" />
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
              <td
                ><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">
                  <TagBadge tag={roster.tag} color={roster.color} />
                </a></td
              >
              <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.name}</a></td>
              <td>
                <GameBadge game={roster.game} />
                <ModeBadge mode={roster.mode} />
              </td>
              <td class="mobile-hide">{new Date(roster.creation_date * 1000).toLocaleString($locale, options)}</td>
            </tr>
          {/each}
        </tbody>
      </Table>
      <PageNavigation
        bind:currentPage={denied_roster_page}
        bind:totalPages={denied_roster_total_pages}
        refresh_function={getDeniedRosters}
      />
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
