<script lang="ts">
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import Table from '$lib/components/common/Table.svelte';
  import type { Tournament } from '$lib/types/tournament';
  import type { MyTournamentRegistration } from '$lib/types/tournaments/my-tournament-registration';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import type { FriendCode } from '$lib/types/friend-code';
  import SquadTournamentFields from './SquadTournamentFields.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import { ChevronDownSolid } from 'flowbite-svelte-icons';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import PlayerName from './PlayerName.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import { check_registrations_open, unregister } from '$lib/util/util';
  import EditMyRegistration from './EditMyRegistration.svelte';

  export let tournament: Tournament;
  export let squad: TournamentSquad;
  export let registration: MyTournamentRegistration;
  export let friend_codes: FriendCode[];

  let edit_reg_dialog: EditMyRegistration;
  let edit_squad_dialog: Dialog;

  let invite_player: PlayerInfo | null = null;

  let registered_players = squad.players.filter((p) => !p.is_invite);
  let invited_players = squad.players.filter((p) => p.is_invite);

  async function invitePlayer(player: PlayerInfo | null) {
    if (!player) {
      return;
    }
    if (!registration.player) {
      return;
    }
    if (!registration.player.is_squad_captain) {
      return;
    }
    const payload = {
      squad_id: registration.player.squad_id,
      player_id: player.id,
      is_representative: false,
    };
    const endpoint = `/api/tournaments/${tournament.id}/invitePlayer`;
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
      alert(`Invitation failed: ${result['title']}`);
    }
  }

  async function cancelInvite(player_id: number) {
    if (!registration.player) {
      return;
    }
    if (!registration.player.is_squad_captain) {
      return;
    }
    let conf = window.confirm('Are you sure you would like to cancel this invite?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: registration.player.squad_id,
      player_id: player_id,
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
      alert(`Cancelling invite failed: ${result['title']}`);
    }
  }

  async function kickPlayer(player_id: number) {
    if (!registration.player) {
      return;
    }
    if (!registration.player.is_squad_captain) {
      return;
    }
    let conf = window.confirm('Are you sure you would like to kick this player?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: registration.player.squad_id,
      player_id: player_id,
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
      alert(`Kicking player failed: ${result['title']}`);
    }
  }

  async function makeCaptain(player_id: number) {
    if (!registration.player) {
      return;
    }
    if (!registration.player.is_squad_captain) {
      return;
    }
    let conf = window.confirm('Are you sure you would like to transfer captain permissions to this player?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: registration.player.squad_id,
      player_id: player_id,
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
      alert(`Transferring captain permissions failed: ${result['title']}`);
    }
  }

  async function unregisterSquad() {
    if (!registration.player) {
      return;
    }
    if (!registration.player.is_squad_captain) {
      return;
    }
    let conf = window.confirm('Are you sure you would like to withdraw your squad from this tournament?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: registration.player.squad_id,
    };
    console.log(payload);
    const endpoint = `/api/tournaments/${tournament.id}/unregisterSquad`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`Failed to unregister: ${result['title']}`);
    }
  }

  async function editSquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const formData = new FormData(event.currentTarget);
    let squad_color = formData.get('squad_color');
    let squad_name = formData.get('squad_name');
    let squad_tag = formData.get('squad_tag');
    const payload = {
      squad_id: squad.id,
      squad_color: Number(squad_color),
      squad_name: squad_name,
      squad_tag: squad_tag,
    };
    const endpoint = `/api/tournaments/${tournament.id}/editMySquad`;
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
      alert(`Editing squad failed: ${result['title']}`);
    }
  }
</script>

<div>My squad</div>

<div>
  {#if tournament.squad_tag_required}
    <TagBadge tag={squad.tag} color={squad.color}/>
  {/if}
  {#if tournament.squad_name_required}
    {squad.name}
  {/if}
</div>
<div>{registered_players.length} players</div>
<Table>
  <col class="country" />
  <col class="name" />
  {#if tournament.mii_name_required}
    <col class="mii-name mobile-hide" />
  {/if}
  <col class="friend-codes mobile-hide" />
  {#if tournament.host_status_required}
    <col class="can-host mobile-hide" />
  {/if}
  <col class="actions" />
  <thead>
    <tr>
      <th />
      <th>Name</th>
      {#if tournament.mii_name_required}
        <th class="mobile-hide">In-Game Name</th>
      {/if}
      <th class="mobile-hide">Friend Codes</th>
      {#if tournament.host_status_required}
        <th class="mobile-hide">Can Host</th>
      {/if}
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {#each registered_players as player, i}
      <tr class="row-{i % 2} {registration.player?.player_id === player.player_id ? "me" : ""}">
        <td>
          <Flag country_code={player.country_code}/>
        </td>
        <td class="name">
          <PlayerName {player}/>
        </td>
        {#if tournament.mii_name_required}
          <td class="mobile-hide">{player.mii_name}</td>
        {/if}
        <td class="mobile-hide">
          {#if player.friend_codes.length > 0}
            {player.friend_codes[0]}
          {/if}
        </td>
        {#if tournament.host_status_required}
          <td class="mobile-hide">{player.can_host ? 'Yes' : 'No'}</td>
        {/if}
        <td>
          {#if check_registrations_open(tournament)}
            <ChevronDownSolid class="cursor-pointer"/>
            <Dropdown>
              {#if registration.player?.player_id === player.player_id}
                {#if tournament.require_single_fc || tournament.mii_name_required || tournament.host_status_required}
                  <DropdownItem on:click={edit_reg_dialog.open}>Edit</DropdownItem>
                {/if}
                <DropdownItem on:click={() => unregister(registration, tournament, squad)}>Unregister</DropdownItem>
              {:else if registration.player?.is_squad_captain}
                <DropdownItem on:click={() => kickPlayer(player.player_id)}>Kick</DropdownItem>
                <DropdownItem on:click={() => makeCaptain(player.player_id)}>Make Captain</DropdownItem>
              {/if}
            </Dropdown>
            
          {/if}
        </td>
      </tr>
    {/each}
  </tbody>
</Table>

{#if invited_players.length > 0}
  <div>{invited_players.length} invited players</div>
  <Table>
    <col class="country" />
    <col class="name" />
    <col class="invite-fcs mobile-hide" />
    <col class="cancel-invite" />

    <thead>
      <tr>
        <th />
        <th>Name</th>
        <th class="mobile-hide">Friend Codes</th>

        <th>Cancel invitation</th>
      </tr>
    </thead>
    <tbody>
      {#each invited_players as player, i}
        <tr class="row-{i % 2}">
          <td><Flag country_code={player.country_code}/></td>
          <td>
            <PlayerName {player}/>
          </td>

          <td class="mobile-hide">
            {#if player.friend_codes.length > 0}
              {player.friend_codes[0]}
            {/if}
          </td>

          <td>
            {#if check_registrations_open(tournament)}
              <Button size="xs" on:click={() => cancelInvite(player.player_id)}>Cancel</Button>
            {/if}
          </td>
        </tr>
      {/each}
    </tbody>
  </Table>
{/if}

{#if check_registrations_open(tournament) && registration.player?.is_squad_captain}
  <!-- If registrations are open and our squad is not full and we are the squad captain -->
  {#if !tournament.max_squad_size || squad.players.length < tournament.max_squad_size}
    <div><b>Invite players</b></div>
    <PlayerSearch
      bind:player={invite_player}
      game={tournament.game}
      squad_id={tournament.team_members_only ? registration.player?.squad_id : null}
    />
    {#if invite_player}
      <div>
        <Button on:click={() => invitePlayer(invite_player)}>Invite Player</Button>
      </div>
    {/if}
  {/if}
  <br />
  <div>
    <Button on:click={edit_squad_dialog.open}>Edit Squad</Button>
    <Button on:click={unregisterSquad}>Unregister Squad</Button>
  </div>
{/if}

<EditMyRegistration bind:this={edit_reg_dialog} {tournament} {friend_codes} {registration}/>

<Dialog bind:this={edit_squad_dialog} header="Edit Squad Registration">
  <form method="POST" on:submit|preventDefault={editSquad}>
    <SquadTournamentFields {tournament} squad_color={squad.color} squad_name={squad.name} squad_tag={squad.tag} />
    <br />
    <div>
      <Button type="submit">Edit Squad</Button>
      <Button type="button" on:click={edit_squad_dialog.close}>Cancel</Button>
    </div>
  </form>
</Dialog>

<style>
  col.country {
    width: 10%;
  }
  col.name {
    width: 25%;
  }
  col.mii-name {
    width: 25%;
  }
  col.friend-codes {
    width: 20%;
  }
  col.invite-fcs {
    width: 40%;
  }
  col.can-host {
    width: 10%;
  }
  col.cancel-invite {
    width: 25%;
  }
  col.actions {
    width: 10%;
  }
</style>
