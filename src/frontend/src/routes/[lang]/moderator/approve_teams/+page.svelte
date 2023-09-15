<script lang="ts">
  import { onMount } from 'svelte';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import type { Team } from '$lib/types/team';
  import { permissions } from '$lib/util/util';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  let teams: Team[] = [];

  onMount(async () => {
    const res = await fetch(`/api/registry/teams/unapprovedTeams`);
    if (res.status !== 200) {
      return;
    }
    const body: Team[] = await res.json();
    teams = body;
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
    alert('Successfully approved team');
    goto(`/${$page.params.lang}/registry/teams`);
  }

  async function denyTeam(team: Team) {
    const res = await fetch(`/api/registry/teams/${team.id}/deny`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    alert('Successfully denied team');
    goto(`/${$page.params.lang}/registry/teams`);
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
