<script lang="ts">
    import { onMount } from 'svelte';
    import type { TeamInviteApproval } from '$lib/types/team-invite';
    import Section from '$lib/components/common/Section.svelte';
    import Table from '$lib/components/common/Table.svelte';
    import { locale } from '$i18n/i18n-svelte';

    let transfers: TeamInviteApproval[] = [];

    onMount(async () => {
        const res = await fetch(`/api/registry/teams/transfers`);
        if (res.status !== 200) {
            return;
        }
        const body: TeamInviteApproval[] = await res.json();
        transfers = body;
    });

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };

    async function approveTransfer(transfer: TeamInviteApproval) {
        const payload = {
            invite_id: transfer.invite_id
        };
        const endpoint = "/api/registry/teams/approveTransfer";
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (res.status < 300) {
            window.location.reload();
        } else {
            alert(`Approving transfer failed: ${result['title']}`);
        }
    }
</script>

<Section header="Transfers">
    {#if transfers.length}
    <Table>
        <col class="player">
        <col class="old_tag">
        <col class="new_tag">
        <col class="date">
        <col class="approve">
        <thead>
            <tr>
                <th>Player</th>
                <th>From</th>
                <th>To</th>
                <th>Date</th>
                <th>Approve?</th>
            </tr>
        </thead>
        <tbody>
            {#each transfers as transfer, i}
                <tr class="row-{i % 2}">
                    <td>{transfer.player_country_code} {transfer.player_name}</td>
                    <td>
                        {#if transfer.roster_leave}
                            {transfer.roster_leave.roster_tag ? transfer.roster_leave.roster_tag : transfer.roster_leave.team_tag}
                        {:else}
                            None
                        {/if}
                    </td>
                    <td>{transfer.roster_tag ? transfer.roster_tag : transfer.team_tag}</td>
                    <td>{new Date(transfer.date * 1000).toLocaleString($locale, options)}</td>
                    <td>
                        <button class="check" on:click={() => approveTransfer(transfer)}>✓</button>
                        <button class="x">X</button>
                    </td>
                </tr>
                
            {/each}
        </tbody>
    </Table>
    {:else}
        No transfers.
    {/if}
</Section>

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
  