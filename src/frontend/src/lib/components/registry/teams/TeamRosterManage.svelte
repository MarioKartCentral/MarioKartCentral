<script lang="ts">
  import type { TeamRoster } from '$lib/types/team-roster';
  import Table from '$lib/components/common/Table.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import type { RosterPlayer } from '$lib/types/roster-player';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import LL from '$i18n/i18n-svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import RosterNameTagRequest from './RosterNameTagRequest.svelte';
  import { ChevronDownSolid } from 'flowbite-svelte-icons';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, check_team_permission, team_permissions, get_highest_team_role_position, permissions } from '$lib/util/permissions';
  import RosterPlayerName from './RosterPlayerName.svelte';
  import BaggerBadge from '$lib/components/badges/BaggerBadge.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import { page } from '$app/stores';

  export let roster: TeamRoster;
  export let is_mod = false;
  let kick_dialog: Dialog;
  let edit_dialog: Dialog;
  let force_edit_dialog: Dialog;
  let curr_player: RosterPlayer;
  let invite_player: PlayerInfo | null;
  let invite_player_bagger: boolean = false;

  let user_info: UserInfo;
    user.subscribe((value) => {
      user_info = value;
    });

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour12: true,
  };

  function can_kick(player: RosterPlayer) {
    let player_hierarchy = 2;
    if(player.is_manager) {
      player_hierarchy = 0;
    }
    else if(player.is_leader) {
      player_hierarchy = 1;
    }
    return get_highest_team_role_position(user_info, roster.team_id) < player_hierarchy;
  }

  async function invitePlayer(player_id: number) {
    const payload = {
      team_id: roster.team_id,
      roster_id: roster.id,
      player_id: player_id,
      is_bagger_clause: invite_player_bagger
    };
    const endpoint = '/api/registry/teams/invitePlayer';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TEAMS.EDIT.PLAYER_INVITE_FAILED()}: ${result['title']}`);
    }
  }

  async function retractInvite(player_id: number) {
    const payload = {
      team_id: roster.team_id,
      roster_id: roster.id,
      player_id: player_id,
    };
    console.log(payload);
    let endpoint: string;
    if(is_mod) {
      endpoint = '/api/registry/teams/forceDeleteInvite';
    }
    else {
      endpoint = '/api/registry/teams/deleteInvite';
    }
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TEAMS.EDIT.DELETE_INVITE_FAILED()}: ${result['title']}`);
    }
  }

  function kickDialog(player: RosterPlayer) {
    curr_player = player;
    kick_dialog.open();
  }

  async function kickPlayer(player: RosterPlayer) {
    console.log(player);
    const payload = {
      player_id: player.player_id,
      roster_id: roster.id,
      team_id: roster.team_id,
    };
    console.log(payload);
    let endpoint: string;
    if(is_mod) {
      endpoint = '/api/registry/teams/forceKickPlayer';
    }
    else {
      endpoint = '/api/registry/teams/kickPlayer';
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TEAMS.EDIT.PLAYER_KICK_FAILED()}: ${result['title']}`);
    }
  }

  async function editRoster(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    edit_dialog.close();
    const data = new FormData(event.currentTarget);
    function getOptionalValue(name: string) {
      return data.get(name) ? data.get(name)?.toString() : '';
    }
    const payload = {
      roster_id: roster.id,
      team_id: roster.team_id,
      is_recruiting: getOptionalValue('recruiting') === 'true' ? true : false,
    };
    const endpoint = '/api/registry/teams/editRoster';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert($LL.TEAMS.EDIT.ROSTER_EDIT_SUCCESS());
    } else {
      alert(`${$LL.TEAMS.EDIT.ROSTER_EDIT_FAILED()}: ${result['title']}`);
    }
  }

  async function forceEditRoster(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    edit_dialog.close();
    const data = new FormData(event.currentTarget);
    function getOptionalValue(name: string) {
      return data.get(name) ? data.get(name)?.toString() : '';
    }
    const payload = {
      roster_id: roster.id,
      name: data.get('name')?.toString(),
      tag: data.get('tag')?.toString(),
      team_id: roster.team_id,
      is_recruiting: getOptionalValue('recruiting') === 'true' ? true : false,
      is_active: getOptionalValue('is_active') === 'true' ? true : false,
      approval_status: data.get('approval_status'),
    };
    const endpoint = '/api/registry/teams/forceEditRoster';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert($LL.TEAMS.EDIT.ROSTER_EDIT_SUCCESS());
    } else {
      alert(`${$LL.TEAMS.EDIT.ROSTER_EDIT_FAILED()}: ${result['title']}`);
    }
  }

  async function grantTeamRole(player: RosterPlayer, role_name: string) {
    let conf = window.confirm($LL.TEAMS.EDIT.TEAM_ROLE_ADD_CONFIRM({player_name: player.name, team_role: role_name}));
    if(!conf) return;
    const payload = {
      player_id: player.player_id,
      role_name: role_name
    }
    const endpoint = `/api/registry/teams/${roster.team_id}/roles/grant`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TEAMS.EDIT.TEAM_ROLE_ADD_FAILED()}: ${result['title']}`);
    }
  }

  async function removeTeamRole(player: RosterPlayer, role_name: string) {
    let conf = window.confirm($LL.TEAMS.EDIT.TEAM_ROLE_REMOVE_CONFIRM({player_name: player.name, team_role: role_name}));
    if(!conf) return;
    const payload = {
      player_id: player.player_id,
      role_name: role_name
    }
    const endpoint = `/api/registry/teams/${roster.team_id}/roles/remove`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TEAMS.EDIT.TEAM_ROLE_REMOVE_FAILED()}: ${result['title']}`);
    }
  }
</script>

<Section header="{roster.name}">
  <div slot="header_content">
    {#if !roster.is_active}
      ({$LL.TEAMS.EDIT.ROSTER_INACTIVE()})
    {/if}
    <TagBadge tag={roster.tag} color={roster.color} />
    <GameBadge game={roster.game}/>
    <ModeBadge mode={roster.mode}/>
    {#if (roster.approval_status === 'approved' && roster.is_active) || is_mod}
      <Button on:click={is_mod ? force_edit_dialog.open : edit_dialog.open}>{$LL.TEAMS.EDIT.EDIT_ROSTER()}</Button>
    {/if}
  </div>
  {roster.players.length}
  {roster.players.length !== 1 ? $LL.TEAMS.PROFILE.PLAYERS() : $LL.TEAMS.PROFILE.PLAYERS()}
  {#if roster.players.length}
    <div class="section">
      <Table>
        <col class="country" />
        <col class="name" />
        <col class="fc mobile-hide" />
        <col class="join_date mobile-hide" />
        <col class="manage_player" />
        <thead>
          <tr>
            <th></th>
            <th>{$LL.COMMON.NAME()}</th>
            <th class="mobile-hide">{$LL.FRIEND_CODES.FRIEND_CODE()}</th>
            <th class="mobile-hide">{$LL.TEAMS.PROFILE.JOIN_DATE()}</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {#each roster.players as player, i}
            <tr class="row-{i % 2} {user_info.player_id === player.player_id ? 'me' : ''}">
              <td><Flag country_code={player.country_code} /></td>
              <td>
                <RosterPlayerName {player}/>
              </td>
              <td class="mobile-hide">{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
              <td class="mobile-hide">{new Date(player.join_date * 1000).toLocaleString($locale, options)}</td>
              <td>
                <ChevronDownSolid class="cursor-pointer"/>
                <Dropdown>
                  {#if can_kick(player)}
                    <DropdownItem on:click={() => kickDialog(player)}>
                      {$LL.TEAMS.EDIT.KICK_PLAYER()}
                    </DropdownItem>
                  {/if}
                  {#if check_team_permission(user_info, team_permissions.manage_team_roles, roster.team_id)}
                    {#if player.is_leader}
                      <DropdownItem on:click={() => removeTeamRole(player, "Leader")}>
                        {$LL.TEAMS.EDIT.REMOVE_LEADER()}
                      </DropdownItem>
                    {:else if !player.is_manager}
                      <DropdownItem on:click={() => grantTeamRole(player, "Leader")}>
                        {$LL.TEAMS.EDIT.MAKE_LEADER()}
                      </DropdownItem>
                    {/if}
                  {/if}
                  {#if check_permission(user_info, team_permissions.manage_team_roles)}
                    {#if player.is_manager}
                      <DropdownItem on:click={() => removeTeamRole(player, "Manager")}>
                        {$LL.TEAMS.EDIT.REMOVE_MANAGER()}
                      </DropdownItem>
                    {:else}
                      <DropdownItem on:click={() => grantTeamRole(player, "Manager")}>
                        {$LL.TEAMS.EDIT.MAKE_MANAGER()}
                      </DropdownItem>
                    {/if}
                  {/if}
                </Dropdown>
              </td>
            </tr>
          {/each}
        </tbody>
      </Table>
    </div>
  {/if}
  {#if (roster.approval_status === 'approved' && roster.is_active) || is_mod}
    {#if roster.invites.length}
      <div class="section">
        <h3>{$LL.TEAMS.EDIT.INVITATIONS()}</h3>
        <Table>
          <col class="country" />
          <col class="name" />
          <col class="fc mobile-hide" />
          <col class="join_date mobile-hide" />
          <col class="manage_player" />
          <thead>
            <tr>
              <th></th>
              <th>{$LL.COMMON.NAME()}</th>
              <th class="mobile-hide">{$LL.FRIEND_CODES.FRIEND_CODE()}</th>
              <th class="mobile-hide">{$LL.TEAMS.PROFILE.JOIN_DATE()}</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {#each roster.invites as player}
              <tr>
                <td><Flag country_code={player.country_code} /></td>
                <td>
                  <a href="/{$page.params.lang}/registry/players/profile?id={player.player_id}">
                    {player.name}
                  </a>
                  {#if player.is_bagger_clause}
                    <BaggerBadge/>
                  {/if}
                </td>
                <td class="mobile-hide">{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
                <td class="mobile-hide">{new Date(player.invite_date * 1000).toLocaleString($locale, options)}</td>
                <td>
                  <Button on:click={() => retractInvite(player.player_id)}>{$LL.TEAMS.EDIT.RETRACT_INVITE()}</Button>
                </td>
              </tr>
            {/each}
          </tbody>
        </Table>
      </div>
    {/if}
    {#if check_permission(user_info, permissions.invite_to_team, true)}
      <div class="section">
        <b>{$LL.TEAMS.EDIT.INVITE_PLAYER()}</b>
        <PlayerSearch bind:player={invite_player} game={roster.game} />
        {#if invite_player}
          {#if roster.game === 'mkw'}
            <div>
              {$LL.COMMON.BAGGER()}?
              <select bind:value={invite_player_bagger}>
                <option value={false}>
                  {$LL.COMMON.NO()}
                </option>
                <option value={true}>
                  {$LL.COMMON.YES()}
                </option>
              </select>
            </div>
          {/if}
          <Button on:click={() => invitePlayer(Number(invite_player?.id))}>{$LL.TEAMS.EDIT.INVITE_PLAYER()}</Button>
        {/if}
      </div>
    {/if}
    
  {:else if roster.approval_status === "pending"}
    <div>
      {$LL.TEAMS.EDIT.ROSTER_PENDING_APPROVAL()}
    </div>
  {/if}
</Section>

<Dialog bind:this={kick_dialog} header={$LL.TEAMS.EDIT.KICK_PLAYER()}>
  {$LL.TEAMS.EDIT.KICK_CONFIRM({player_name: curr_player?.name})}
  <div>
    <Button on:click={() => kickPlayer(curr_player)}>{$LL.TEAMS.EDIT.KICK()}</Button>
    <Button on:click={kick_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
  </div>
</Dialog>

<Dialog bind:this={edit_dialog} header={$LL.TEAMS.EDIT.EDIT_ROSTER()}>
  <RosterNameTagRequest {roster}/>
  <br/>
  <form method="post" on:submit|preventDefault={editRoster}>
    <label for="recruiting">{$LL.TEAMS.EDIT.RECRUITMENT_STATUS()}</label>
    <select name="recruiting">
      <option value="true">{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.RECRUITING()}</option>
      <option value="false">{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.NOT_RECRUITING()}</option>
    </select>
    <br />
    <Button type="submit">{$LL.COMMON.SUBMIT()}</Button>
  </form>
</Dialog>

<Dialog bind:this={force_edit_dialog} header={$LL.TEAMS.EDIT.EDIT_ROSTER()}>
  <form method="post" on:submit|preventDefault={forceEditRoster}>
    <label for="name">{$LL.TEAMS.EDIT.ROSTER_NAME()}</label>
    <input name="name" type="text" value={roster.name} required pattern="^\S.*\S$|^\S$"/>
    <br />
    <label for="tag">{$LL.TEAMS.EDIT.ROSTER_TAG()}</label>
    <input name="tag" type="text" value={roster.tag} required pattern="^\S.*\S$|^\S$"/>
    <label for="recruiting">{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.STATUS()}</label>
    <select name="recruiting">
      <option value="true">{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.RECRUITING()}</option>
      <option value="false">{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.NOT_RECRUITING()}</option>
    </select>
    <br />
    <label for="approval_status">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.STATUS()}</label>
    <select name="approval_status" value={roster.approval_status}>
      <option value="approved">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.APPROVED()}</option>
      <option value="denied">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.DENIED()}</option>
      <option value="pending">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.PENDING()}</option>
    </select>
    <br />
    <label for="is_active">{$LL.TEAMS.PROFILE.ACTIVE_HISTORICAL()}</label>
    <select name="is_active" value={roster.is_active ? 'true' : 'false'}>
      <option value="true">{$LL.TEAMS.PROFILE.ACTIVE()}</option>
      <option value="false">{$LL.TEAMS.PROFILE.HISTORICAL()}</option>
    </select>
    <br />
    <Button type="submit">{$LL.TEAMS.EDIT.EDIT_ROSTER()}</Button>
  </form>
</Dialog>

<style>
  col.country {
    width: 10%;
  }
  col.name {
    width: 30%;
  }
  col.fc {
    width: 20%;
  }
  col.join_date {
    width: 20%;
  }
  col.manage_player {
    width: 20%;
  }
  div.section {
    margin: 10px 0;
  }
</style>