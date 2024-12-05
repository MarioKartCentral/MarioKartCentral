<script lang="ts">
    import Table from "$lib/components/common/Table.svelte";
    import type { TeamInvite } from "$lib/types/team-invite";
    import { locale } from "$i18n/i18n-svelte";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import Dialog from "$lib/components/common/Dialog.svelte";
    import TagBadge from "$lib/components/badges/TagBadge.svelte";
    import ConfirmButton from "$lib/components/common/buttons/ConfirmButton.svelte";
    import CancelButton from "$lib/components/common/buttons/CancelButton.svelte";
    import GameBadge from "$lib/components/badges/GameBadge.svelte";
    import ModeBadge from "$lib/components/badges/ModeBadge.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import BaggerBadge from "$lib/components/badges/BaggerBadge.svelte";
    import { check_permission, permissions } from "$lib/util/permissions";
    import LL from "$i18n/i18n-svelte";

    export let invites: TeamInvite[];

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let accept_dialog: Dialog;
    let decline_dialog: Dialog;
    let curr_invite: TeamInvite;
    let leave_roster_id: number | null = null;

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
        if (!user_info.player) {
            return [];
        }
        console.log(user_info.player.rosters);
        console.log(invite);
        let rosters = user_info.player.rosters.filter((r) => r.game === invite.game && r.mode === invite.mode && r.is_bagger_clause === Boolean(invite.is_bagger_clause));
        console.log(rosters);
        return rosters;
    }

    $: leaveable_rosters = curr_invite ? getLeaveableRosters(curr_invite) : [];

    async function acceptInvite(invite: TeamInvite) {
        if(leaveable_rosters.length && !leave_roster_id) {
            alert($LL.INVITES.SELECT_LEAVE_ROSTER_ERROR());
            return;
        }
        accept_dialog.close();
        const payload = {
            invite_id: invite.invite_id,
            roster_leave_id: leave_roster_id,
        };
        const res = await fetch(`/api/registry/teams/acceptInvite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (res.status < 300) {
            alert($LL.INVITES.ACCEPT_TEAM_INVITE_SUCCESS({roster_name: invite.roster_name}));
            window.location.reload();
        } else {
            alert(`${$LL.INVITES.ACCEPT_TEAM_INVITE_FAILED()}: ${result['title']}`);
        }
    }
    async function declineInvite(invite: TeamInvite) {
        decline_dialog.close();
        const payload = {
            invite_id: invite.invite_id,
        };
        const res = await fetch(`/api/registry/teams/declineInvite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (res.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.INVITES.DECLINE_TEAM_INVITE_FAILED()}: ${result['title']}`);
        }
    }
</script>

{#if invites.length}
    <Table>
    <col class="tag" />
    <col class="name" />
    <col class="mode mobile-hide"/>
    <col class="date mobile-hide" />
    <col class="accept" />
    <thead>
        <tr>
        <th>{$LL.TAG()}</th>
        <th>{$LL.NAME()}</th>
        <th class="mode mobile-hide">{$LL.MODE()}</th>
        <th class="mode mobile-hide">{$LL.DATE()}</th>
        <th>{$LL.INVITES.ACCEPT()}?</th>
        </tr>
    </thead>
    <tbody>
        {#each invites as invite}
        <tr>
            <td>
                <TagBadge tag={invite.roster_tag ? invite.roster_tag : invite.team_tag} color={invite.team_color}/>
            </td>
            <td>
                {invite.roster_name}
                {#if invite.is_bagger_clause}
                    <BaggerBadge/>
                {/if}
            </td>
            <td class="mode mobile-hide">
                <GameBadge game={invite.game}/>
                <ModeBadge mode={invite.mode}/>
            </td>
            <td class="mode mobile-hide">{new Date(invite.date * 1000).toLocaleString($locale, options)}</td>
            <td>
            {#if check_permission(user_info, permissions.join_team, true)}
                <ConfirmButton on:click={() => acceptDialog(invite)}/>
            {/if}
            <CancelButton on:click={() => declineDialog(invite)}/>
            </td>
        </tr>
        {/each}
    </tbody>
    </Table>
{:else}
    {$LL.INVITES.NO_INVITES()}
{/if}

<Dialog bind:this={accept_dialog} header={$LL.INVITES.ACCEPT_TEAM_INVITE()}>
    {$LL.INVITES.ACCEPT_TEAM_INVITE_CONFIRM({roster_name: curr_invite?.roster_name})}
    <br /><br />
    {#if leaveable_rosters.length}
      {$LL.INVITES.SELECT_LEAVE_ROSTER()}
      <select bind:value={leave_roster_id}>
        {#each leaveable_rosters as r}
          <option value={r.roster_id}>{r.roster_name}</option>
        {/each}
      </select>
    {/if}
    <div class="accept">
      <Button on:click={() => acceptInvite(curr_invite)}>{$LL.INVITES.ACCEPT()}</Button>
      <Button on:click={accept_dialog.close}>Cancel</Button>
    </div>
  </Dialog>
  
  <Dialog bind:this={decline_dialog} header="Decline Team Invite">
    {$LL.INVITES.DECLINE_TEAM_INVITE_CONFIRM({roster_name: curr_invite?.roster_name})}
    <br /><br />
    <div class="accept">
      <Button on:click={() => declineInvite(curr_invite)}>{$LL.INVITES.DECLINE()}</Button>
      <Button on:click={decline_dialog.close}>{$LL.INVITES.CANCEL()}</Button>
    </div>
  </Dialog>

<style>
    col.tag {
        width: 15%;
    }
    col.name {
        width: 25%;
    }
    col.mode {
        width: 25%;
    }
    col.date {
        width: 15%;
    }
    col.accept {
        width: 20%;
    }
    div.accept {
        margin-top: 20px;
    }
</style>