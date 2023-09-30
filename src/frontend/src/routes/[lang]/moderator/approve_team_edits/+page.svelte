<script lang="ts">
    import { onMount } from 'svelte';
    import Section from '$lib/components/common/Section.svelte';
    import Table from '$lib/components/common/Table.svelte';
    import type { TeamEditRequest } from '$lib/types/team-edit-request';
    import type { RosterEditRequest } from '$lib/types/roster-edit-request';
    import { permissions } from '$lib/util/util';
    import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
    import { locale } from '$i18n/i18n-svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
  
    let team_requests: TeamEditRequest[] = [];
    let roster_requests: RosterEditRequest[] = [];

    onMount(async () => {
      const team_res = await fetch(`/api/registry/teams/changeRequests`);
      if (team_res.status === 200) {
        const body: TeamEditRequest[] = await team_res.json();
        team_requests = body;
      }
      
      const roster_res = await fetch('/api/registry/teams/rosterChangeRequests');
      if (roster_res.status === 200) {
        const body: RosterEditRequest[] = await roster_res.json();
        roster_requests = body;
      }
    });
  
    const options: Intl.DateTimeFormatOptions = {
      dateStyle: 'short',
      timeStyle: 'short',
    };
  
    async function approveTeamRequest(request: TeamEditRequest) {
      const payload = {
        request_id: request.id
      };
      const res = await fetch(`/api/registry/teams/approveChange`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json()
      if (res.status < 300) {
        alert('Successfully approved team profile change');
        goto(`/${$page.params.lang}/registry/teams`);
      } else {
        alert(`Team edit failed: ${result['title']}`);
        }
    }
  
    async function denyTeamRequest(request: TeamEditRequest) {
      const payload = {
        request_id: request.id
      };
      const res = await fetch(`/api/registry/teams/denyChange`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json()
      if (res.status < 300) {
        alert('Successfully denied team profile change');
        goto(`/${$page.params.lang}/registry/teams`);
      } else {
        alert(`Failed: ${result['title']}`);
        }
    }

    async function approveRosterRequest(request: RosterEditRequest) {
      const payload = {
        request_id: request.id
      };
      const res = await fetch(`/api/registry/teams/approveRosterChange`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json()
      if (res.status < 300) {
        alert('Successfully approved roster profile change');
        goto(`/${$page.params.lang}/registry/teams`);
      } else {
        alert(`Team edit failed: ${result['title']}`);
        }
    }

    async function denyRosterRequest(request: RosterEditRequest) {
      const payload = {
        request_id: request.id
      };
      const res = await fetch(`/api/registry/teams/denyRosterChange`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json()
      if (res.status < 300) {
        alert('Successfully denied roster profile change');
        goto(`/${$page.params.lang}/registry/teams`);
      } else {
        alert(`Failed: ${result['title']}`);
        }
    }
  </script>
  
  <PermissionCheck permission={permissions.manage_teams}>
    <Section header="Pending Team Edit Requests">
      <Table>
        <col class="old_tag" />
        <col class="old_name" />
        <col class="new_tag" />
        <col class="new_name" />
        <col class="date" />
        <col class="approve" />
        <thead>
          <tr>
            <th>Old Tag</th>
            <th>Old Name</th>
            <th>New Tag</th>
            <th>New Name</th>
            <th>Date</th>
            <th>Approve?</th>
          </tr>
        </thead>
        <tbody>
            {#each team_requests as r, i}
            <tr class="row-{i % 2}">
                <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.old_tag}</a></td>
                <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.old_name}</a></td>
                <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.new_tag}</a></td>
                <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.new_name}</a></td>
                <td>{new Date(r.date * 1000).toLocaleString($locale, options)}</td>
                <td>
                  <button class="check" on:click={() => approveTeamRequest(r)}>✓</button>
                  <button class="x" on:click={() => denyTeamRequest(r)}>X</button>
                </td>
              </tr>
            {/each}
        </tbody>
      </Table>
    </Section>

    <Section header="Pending Roster Edit Requests">
        <Table>
            <col class="old_tag" />
            <col class="old_name" />
            <col class="new_tag" />
            <col class="new_name" />
            <col class="date" />
            <col class="approve" />
            <thead>
              <tr>
                <th>Old Tag</th>
                <th>Old Name</th>
                <th>New Tag</th>
                <th>New Name</th>
                <th>Date</th>
                <th>Approve?</th>
              </tr>
            </thead>
            <tbody>
                {#each roster_requests as r, i}
                <tr class="row-{i % 2}">
                    <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.old_tag}</a></td>
                    <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.old_name}</a></td>
                    <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.new_tag}</a></td>
                    <td><a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">{r.new_name}</a></td>
                    <td>{new Date(r.date * 1000).toLocaleString($locale, options)}</td>
                    <td>
                      <button class="check" on:click={() => approveRosterRequest(r)}>✓</button>
                      <button class="x" on:click={() => denyRosterRequest(r)}>X</button>
                    </td>
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
  