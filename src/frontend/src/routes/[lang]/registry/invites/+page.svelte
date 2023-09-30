<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import Dialog from "$lib/components/common/Dialog.svelte";
    import { locale } from '$i18n/i18n-svelte';
    import Table from "$lib/components/common/Table.svelte";
    import type { PlayerInvites } from "$lib/types/player-invites";
    import type { TeamInvite } from "$lib/types/team-invite";
    import { onMount } from 'svelte';
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let invites: PlayerInvites;
    let curr_invite: TeamInvite;
    let leave_roster_id: number | null = null;
    let accept_dialog: Dialog;
    let decline_dialog: Dialog;

    onMount(async () => {
        const res = await fetch(`/api/user/me/invites`);
        if (res.status != 200) {
            return;
        }
        const body: PlayerInvites = await res.json();
        invites = body;
    });

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };

    function acceptDialog(invite: TeamInvite) {
        curr_invite = invite;
        accept_dialog.open();
    }

    function declineDialog(invite: TeamInvite) {
        curr_invite = invite;
        decline_dialog.open();
    }

    function getLeaveableRosters(invite: TeamInvite) {
        if(!user_info.player) {
            return [];
        }
        let rosters = user_info.player.rosters.filter((r) => r.game === invite.game && r.mode === invite.mode);
        return rosters;
    }

    $: leaveable_rosters = curr_invite ? getLeaveableRosters(curr_invite) : [];

    async function acceptInvite(invite: TeamInvite) {
        const payload = {
            invite_id: invite.invite_id,
            roster_leave_id: leave_roster_id
        }
        const res = await fetch(`/api/registry/teams/acceptInvite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (res.status < 300) {
            alert(`Successfully accepted invite to ${curr_invite.roster_name ? curr_invite.roster_name : curr_invite.team_name}`)
            window.location.reload();
        } else {
            alert(`Accepting invite failed: ${result['title']}`);
        }
    }
</script>

{#if invites}
    <Section header="Team Invites">
        {#if invites.team_invites.length}
        <Table>
            <col class="tag" />
            <col class="name" />
            <col class="date" />
            <col class="accept" />
            <thead>
                <tr>
                <th>Tag</th>
                <th>Name</th>
                <th>Mode</th>
                <th>Date</th>
                <th>Accept?</th>
                </tr>
            </thead>
            <tbody>
                {#each invites.team_invites as invite}
                    <tr>
                        <td>{invite.roster_tag ? invite.roster_tag : invite.team_tag}</td>
                        <td>{invite.roster_name ? invite.roster_name : invite.team_name}</td>
                        <td>{invite.game} {invite.mode}</td>
                        <td>{new Date(invite.date * 1000).toLocaleString($locale, options)}</td>
                        <td>
                            <button class="check" on:click={() => acceptDialog(invite)}>✓</button>
                            <button class="x" on:click={() => declineDialog(invite)}>X</button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </Table>
        {:else}
            No invites.
        {/if}
    </Section>
    

    <Section header="Tournament Invites">

    </Section>
{/if}

<Dialog bind:this={accept_dialog} header="Accept Team Invite">
    Are you sure you would like to accept the invite to {curr_invite?.team_name}?
    <br/><br/>
        {#if leaveable_rosters.length}
            Select a roster to leave:
            <select bind:value={leave_roster_id}>
                {#each leaveable_rosters as r}
                    <option value={r.roster_id}>{r.roster_name ? r.roster_name : r.team_name}</option>
                {/each}
                <option value={null}>None</option>
            </select>
            {#if !leave_roster_id}
                <div>NOTE: Selecting to not leave a roster may result in your transfer being denied.</div>
            {/if}
        {/if}
    <div>
        <button on:click={() => acceptInvite(curr_invite)}>Accept</button>
        <button on:click={accept_dialog.close}>Cancel</button>
    </div>
</Dialog>

<Dialog bind:this={decline_dialog} header="Decline Team Invite">
    Are you sure you would like to decline the invite to {curr_invite?.team_name}?
    <br/><br/>
    <div>
        <button>Decline</button>
        <button on:click={decline_dialog.close}>Cancel</button>
    </div>
</Dialog>

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
  