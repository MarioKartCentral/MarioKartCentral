<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentPlayer } from '$lib/types/tournament-player';
  import Table from '$lib/components/common/Table.svelte';
  import Flag from '../common/Flag.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import PlayerName from './registration/PlayerName.svelte';
  import { ChevronDownSolid } from 'flowbite-svelte-icons';
  import Dropdown from '../common/Dropdown.svelte';
  import DropdownItem from '../common/DropdownItem.svelte';
  import { check_registrations_open } from '$lib/util/util';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
  import EditPlayerRegistration from './registration/EditPlayerRegistration.svelte';
  import FriendCodeDisplay from '../common/FriendCodeDisplay.svelte';
  import type { RegistrationDetails } from '$lib/types/tournaments/my-tournament-registration';
  import LL from '$i18n/i18n-svelte';

  export let tournament: Tournament;
  export let players: TournamentPlayer[];
  export let is_privileged = false;
  export let registration: RegistrationDetails | null = null;
  export let exclude_invites = true;

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  let edit_reg_dialog: EditPlayerRegistration;

  function get_players() {
    if(!exclude_invites) {
      return players;
    }
    return players.filter((p) => !p.is_invite);
  }

  async function unregisterPlayer(player: TournamentPlayer) {
    const conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_PLAYER_CONFIRM({player_name: player.name}));
    if (!conf) {
      return;
    }
    const payload = {
      registration_id: player.registration_id,
      player_id: player.player_id
    };
    console.log(payload);
    const endpoint = `/api/tournaments/${tournament.id}/forceUnregister`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_PLAYER_FAILED()}: ${result['title']}`);
    }
  }

  async function kickPlayer(player: TournamentPlayer) {
    let conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.KICK_PLAYER_CONFIRM({player_name: player.name}));
    if (!conf) {
      return;
    }
    const payload = {
      registration_id: player.registration_id,
      player_id: player.player_id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/kickPlayer`;
    console.log(payload);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.KICK_PLAYER_FAILED()}: ${result['title']}`);
    }
  }

  async function makeCaptain(player: TournamentPlayer) {
    let conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.MAKE_CAPTAIN_CONFIRM({player_name: player.name}));
    if (!conf) {
      return;
    }
    const payload = {
      registration_id: player.registration_id,
      player_id: player.player_id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/makeCaptain`;
    console.log(payload);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.MAKE_CAPTAIN_FAILED()}: ${result['title']}`);
    }
  }

  async function addRepresentative(player: TournamentPlayer) {
    const payload = {
      registration_id: player.registration_id,
      player_id: player.player_id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/addRepresentative`;
    console.log(payload);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.MAKE_REPRESENTATIVE_FAILED()}: ${result['title']}`);
    }
  }

  async function removeRepresentative(player: TournamentPlayer) {
    const payload = {
      registration_id: player.registration_id,
      player_id: player.player_id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/removeRepresentative`;
    console.log(payload);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.REMOVE_REPRESENTATIVE_FAILED()}: ${result['title']}`);
    }
  }

  async function unregister() {
    if (!registration || !registration.player) {
      return;
    }
    if (registration.player.is_squad_captain) {
      alert($LL.TOURNAMENTS.REGISTRATIONS.CAPTAIN_UNREGISTER_ERROR());
      return;
    }
    const conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_CONFIRM());
    if (!conf) {
      return;
    }
    const payload = {
      registration_id: registration.squad.id,
    };
    console.log(payload);
    const endpoint = `/api/tournaments/${tournament.id}/unregister`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_FAILED()}: ${result['title']}`);
    }
  }
</script>

<Table>
  <col class="country" />
  <col class="name" />
  {#if tournament.mii_name_required && exclude_invites}
    <col class="mii-name mobile-hide" />
  {/if}
  <col class="friend-codes mobile-hide" />
  {#if tournament.host_status_required && exclude_invites}
    <col class="can-host mobile-hide" />
  {/if}
  {#if tournament.checkins_enabled}
    <col class="is-checked-in mobile-hide"/>
  {/if}
  {#if is_privileged || registration}
    <col class="actions"/>
  {/if}
  <thead>
    <tr>
      <th />
      <th>{$LL.COMMON.NAME()}</th>
      {#if tournament.mii_name_required && exclude_invites}
        <th class="mobile-hide">{$LL.TOURNAMENTS.REGISTRATIONS.IN_GAME_NAME}</th>
      {/if}
      <th class="mobile-hide">{$LL.FRIEND_CODES.FRIEND_CODES()}</th>
      {#if tournament.host_status_required && exclude_invites}
        <th class="mobile-hide">{$LL.TOURNAMENTS.REGISTRATIONS.CAN_HOST()}</th>
      {/if}
      {#if tournament.checkins_enabled}
        <th class="mobile-hide">{$LL.TOURNAMENTS.REGISTRATIONS.CHECKED_IN()}</th>
      {/if}
      {#if is_privileged || registration}
        <th/>
      {/if}
    </tr>
  </thead>
  <tbody>
    {#each get_players() as player, i}
      <tr class="row-{i % 2} {user_info.player?.id === player.player_id ? "me" : ""}">
        <td>
          <Flag country_code={player.country_code}/>
        </td>
        <td>
          <PlayerName player_id={player.player_id} name={player.name} is_squad_captain={player.is_squad_captain} is_representative={player.is_representative}
          is_bagger_clause={player.is_bagger_clause} is_eligible={player.is_eligible}/>
        </td>
        {#if tournament.mii_name_required && exclude_invites}
          <td class="mobile-hide">{player.mii_name}</td>
        {/if}
        <td class="mobile-hide">
          {#if player.friend_codes.length > 0}
            <FriendCodeDisplay friend_codes={player.friend_codes} selected_fc_id={player.selected_fc_id}/>
          {/if}
        </td>
        {#if tournament.host_status_required && exclude_invites}
          <td class="mobile-hide">{player.can_host ? 'Yes' : 'No'}</td>
        {/if}
        {#if tournament.checkins_enabled}
          <td class="mobile-hide">{player.is_checked_in ? 'Yes' : 'No'}</td>
        {/if}
        
        {#if is_privileged || registration}
          <td>
            {#if is_privileged}
              <ChevronDownSolid class="cursor-pointer"/>
              <Dropdown>
                <DropdownItem on:click={() => edit_reg_dialog.open(player, true)}>{$LL.COMMON.EDIT()}</DropdownItem>
                <DropdownItem on:click={() => unregisterPlayer(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.REMOVE()}</DropdownItem>
              </Dropdown>
            {:else if user_info.player_id === player.player_id && check_registrations_open(tournament)}
              <ChevronDownSolid class="cursor-pointer"/>
              <Dropdown>
                {#if check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true) &&
                  (tournament.require_single_fc || tournament.mii_name_required || tournament.host_status_required)}
                  <DropdownItem on:click={() => edit_reg_dialog.open(player)}>{$LL.COMMON.EDIT()}</DropdownItem>
                {/if}
                {#if registration && registration.is_squad_captain && registration.squad.id === player.registration_id && !player.is_squad_captain}
                  <DropdownItem on:click={() => makeCaptain(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.MAKE_CAPTAIN()}</DropdownItem>
                {/if}
                <DropdownItem on:click={unregister}>{$LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER()}</DropdownItem>
              </Dropdown>
            {:else if registration && registration.is_squad_captain && registration.squad.id === player.registration_id && check_registrations_open(tournament)}
              <ChevronDownSolid class="cursor-pointer"/>
              <Dropdown>
                <DropdownItem on:click={() => kickPlayer(player)}>
                  {player.is_invite ? $LL.TOURNAMENTS.REGISTRATIONS.RETRACT_INVITE() : $LL.TOURNAMENTS.REGISTRATIONS.KICK_PLAYER()}
                </DropdownItem>
                {#if !player.is_invite}
                  <DropdownItem on:click={() => makeCaptain(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.MAKE_CAPTAIN()}</DropdownItem>
                  {#if (tournament.min_representatives && tournament.min_representatives > 0) || (tournament.max_representatives && tournament.max_representatives > 0)}
                    {#if !player.is_representative}
                      <DropdownItem on:click={() => addRepresentative(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.MAKE_REPRESENTATIVE()}</DropdownItem>
                    {:else}
                      <DropdownItem on:click={() => removeRepresentative(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.REMOVE_REPRESENTATIVE()}</DropdownItem>
                    {/if}
                  {/if}
                {/if}
              </Dropdown>
            {/if}
          </td>
        {/if}
      </tr>
    {/each}
  </tbody>
</Table>

<EditPlayerRegistration bind:this={edit_reg_dialog} {tournament}/>

<style>
  col.country {
    width: 10%;
  }
  col.name {
    width: 25%;
  }
  col.mii-name {
    width: 20%;
  }
  col.friend-codes {
    width: 15%;
  }
  col.can-host {
    width: 10%;
  }
  col.is-checked-in {
    width: 10%;
  }
  col.actions {
    width: 10%;
  }
</style>
