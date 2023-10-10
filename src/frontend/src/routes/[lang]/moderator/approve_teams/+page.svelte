<script lang="ts">
  import { onMount } from 'svelte';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import type { Team } from '$lib/types/team';
  import type { TeamRoster } from '$lib/types/team-roster';
  import { permissions } from '$lib/util/util';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';

  let teams: Team[] = [];
  let rosters: TeamRoster[] = [];

  onMount(async () => {
    const res = await fetch(`/api/registry/teams/unapprovedTeams`);
    if (res.status === 200) {
      const body: Team[] = await res.json();
      teams = body;
    }

    const res2 = await fetch(`/api/registry/teams/unapprovedRosters`);
    if (res2.status === 200) {
      const body: TeamRoster[] = await res2.json();
      rosters = body;
    }
  });

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };

  async function approveTeam(team: Team) {
    const res = await fetch(`/api/registry/teams/${team.id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      alert('Successfully approved team');
      window.location.reload();
    } else {
      alert(`Approving team failed: ${result['title']}`);
    }
  }

  async function denyTeam(team: Team) {
    const res = await fetch(`/api/registry/teams/${team.id}/deny`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      alert('Successfully denied team');
      window.location.reload();
    } else {
      alert(`Denying team failed: ${result['title']}`);
    }
  }

  async function approveRoster(roster: TeamRoster) {
    const res = await fetch(`/api/registry/teams/${roster.team_id}/approveRoster/${roster.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      alert('Successfully approved roster');
      window.location.reload();
    } else {
      alert(`Approving roster failed: ${result['title']}`);
    }
  }

  async function denyRoster(roster: TeamRoster) {
    const res = await fetch(`/api/registry/teams/${roster.team_id}/denyRoster/${roster.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await res.json();
    if (res.status < 300) {
      alert('Successfully denied roster');
      window.location.reload();
    } else {
      alert(`Denying roster failed: ${result['title']}`);
    }
  }
</script>

<PermissionCheck permission={permissions.manage_teams}>
  <Section header="Pending Teams">
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="date" />
      <col class="approve" />
      <thead>
        <tr>
          <th>Tag</th>
          <th>Name</th>
          <th>Date</th>
          <th>Approve?</th>
        </tr>
      </thead>
      <tbody>
        {#each teams.filter((t) => t.is_approved === 'pending') as team, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.tag}</a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a></td>
            <td>{new Date(team.creation_date * 1000).toLocaleString($locale, options)}</td>
            <td>
              <button class="check" on:click={() => approveTeam(team)}>✓</button>
              <button class="x" on:click={() => denyTeam(team)}>X</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </Table>
  </Section>
  <Section header="Pending Rosters">
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="date" />
      <col class="approve" />
      <thead>
        <tr>
          <th>Tag</th>
          <th>Name</th>
          <th>Date</th>
          <th>Approve?</th>
        </tr>
      </thead>
      <tbody>
        {#each rosters.filter((r) => r.is_approved === 'pending') as roster, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.tag}</a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.name}</a></td>
            <td>{new Date(roster.creation_date * 1000).toLocaleString($locale, options)}</td>
            <td>
              <button class="check" on:click={() => approveRoster(roster)}>✓</button>
              <button class="x" on:click={() => denyRoster(roster)}>X</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </Table>
  </Section>
  <Section header="Denied Teams">
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="date" />
      <thead>
        <tr>
          <th>Tag</th>
          <th>Name</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {#each teams.filter((t) => t.is_approved === 'denied') as team, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.tag}</a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a></td>
            <td>{new Date(team.creation_date * 1000).toLocaleString($locale, options)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
  </Section>
  <Section header="Denied Rosters">
    <Table>
      <col class="tag" />
      <col class="name" />
      <col class="date" />
      <thead>
        <tr>
          <th>Tag</th>
          <th>Name</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {#each rosters.filter((t) => t.is_approved === 'denied') as roster, i}
          <tr class="row-{i % 2}">
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.tag}</a></td>
            <td><a href="/{$page.params.lang}/registry/teams/profile?id={roster.team_id}">{roster.name}</a></td>
            <td>{new Date(roster.creation_date * 1000).toLocaleString($locale, options)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
  </Section>
</PermissionCheck>

<style>
  button {
    min-width: 50px;
  }
  .check {
    background-color: green;
  }
  .x {
    background-color: red;
  }
</style>
