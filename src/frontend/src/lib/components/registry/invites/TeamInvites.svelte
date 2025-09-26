<script lang="ts">
  import type { TeamInvite } from '$lib/types/team-invite';
  import { locale } from '$i18n/i18n-svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import ConfirmButton from '$lib/components/common/buttons/ConfirmButton.svelte';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import BaggerBadge from '$lib/components/badges/BaggerBadge.svelte';
  import { check_permission, permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';
  import { page } from '$app/stores';

  export let invites: TeamInvite[];

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  let accept_dialog: Dialog;
  let decline_dialog: Dialog;
  let curr_invite: TeamInvite;
  let leave_roster_id: number | null = null;
  let working = false;

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
    let rosters = user_info.player.rosters.filter(
      (r) =>
        r.game === invite.game && r.mode === invite.mode && r.is_bagger_clause === Boolean(invite.is_bagger_clause),
    );
    console.log(rosters);
    return rosters;
  }

  $: leaveable_rosters = curr_invite ? getLeaveableRosters(curr_invite) : [];

  async function acceptInvite(invite: TeamInvite) {
    working = true;
    if (leaveable_rosters.length && !leave_roster_id) {
      alert($LL.INVITES.SELECT_LEAVE_ROSTER_ERROR());
      working = false;
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
    working = false;
    const result = await res.json();
    if (res.status < 300) {
      alert($LL.INVITES.ACCEPT_TEAM_INVITE_SUCCESS({ roster_name: invite.roster_name }));
      window.location.reload();
    } else {
      alert(`${$LL.INVITES.ACCEPT_TEAM_INVITE_FAILED()}: ${result['title']}`);
    }
  }
  async function declineInvite(invite: TeamInvite) {
    working = true;
    decline_dialog.close();
    const payload = {
      invite_id: invite.invite_id,
    };
    const res = await fetch(`/api/registry/teams/declineInvite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.INVITES.DECLINE_TEAM_INVITE_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if invites.length}
  <div class="invites">
    {#each invites as invite}
      <div class="row">
        <div class="date field">
          {new Date(invite.date * 1000).toLocaleString($locale, options)}
        </div>
        <div class="left field">
          <a href="/{$page.params.lang}/registry/teams/profile?id={invite.team_id}">
            <TagBadge tag={invite.roster_tag ? invite.roster_tag : invite.team_tag} color={invite.team_color} />
          </a>
          <div>
            <a href="/{$page.params.lang}/registry/teams/profile?id={invite.team_id}">
              {invite.roster_name}
              {#if invite.is_bagger_clause}
                <BaggerBadge />
              {/if}
            </a>
          </div>
        </div>
        <div class="badges field">
          <GameBadge game={invite.game} />
          <ModeBadge mode={invite.mode} />
        </div>
        <div class="accept field">
          {#if check_permission(user_info, permissions.join_team, true)}
            <ConfirmButton on:click={() => acceptDialog(invite)} />
          {/if}
          <CancelButton on:click={() => declineDialog(invite)} />
        </div>
      </div>
    {/each}
  </div>
{:else}
  {$LL.INVITES.NO_INVITES()}
{/if}

<Dialog bind:this={accept_dialog} header={$LL.INVITES.ACCEPT_TEAM_INVITE()}>
  {$LL.INVITES.ACCEPT_TEAM_INVITE_CONFIRM({ roster_name: curr_invite?.roster_name })}
  <br /><br />
  {#if leaveable_rosters.length}
    {$LL.INVITES.SELECT_LEAVE_ROSTER()}
    <select bind:value={leave_roster_id}>
      {#each leaveable_rosters as r}
        <option value={r.roster_id}>{r.roster_name}</option>
      {/each}
    </select>
  {/if}
  <div class="dialog-accept">
    <Button {working} on:click={() => acceptInvite(curr_invite)}>{$LL.INVITES.ACCEPT()}</Button>
    <Button on:click={accept_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
  </div>
</Dialog>

<Dialog bind:this={decline_dialog} header={$LL.INVITES.DECLINE()}>
  {$LL.INVITES.DECLINE_TEAM_INVITE_CONFIRM({ roster_name: curr_invite?.roster_name })}
  <br /><br />
  <div class="dialog-accept">
    <Button {working} on:click={() => declineInvite(curr_invite)}>{$LL.INVITES.DECLINE()}</Button>
    <Button on:click={decline_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
  </div>
</Dialog>

<style>
  .invites {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  .row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    align-items: center;
    font-size: 0.9rem;
    background-color: rgba(255, 255, 255, 0.15);
    padding: 12px;
    min-height: 75px;
  }
  .row:nth-child(odd) {
    background-color: rgba(210, 210, 210, 0.15);
  }
  .date {
    min-width: 200px;
  }
  .field {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 5px;
  }
  .left {
    min-width: 200px;
  }
  .badges {
    min-width: 200px;
  }
  .accept {
    min-width: 100px;
  }
  div.dialog-accept {
    margin-top: 20px;
  }
</style>
