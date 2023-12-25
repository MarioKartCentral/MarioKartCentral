<script lang="ts">
  import type { TeamRoster } from '$lib/types/team-roster';
  import Table from '$lib/components/common/Table.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import type { RosterPlayer } from '$lib/types/roster-player';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import type { PlayerInfo } from '$lib/types/player-info';

  export let roster: TeamRoster;
  let kick_dialog: Dialog;
  let edit_dialog: Dialog;
  let curr_player: RosterPlayer;
  let invite_player: PlayerInfo | null;

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour12: true,
  };

  async function invitePlayer(player_id: number) {
    const payload = {
      team_id: roster.team_id,
      roster_id: roster.id,
      player_id: player_id,
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
      alert(`Player invite failed: ${result['title']}`);
    }
  }

  async function retractInvite(player_id: number) {
    const payload = {
      team_id: roster.team_id,
      roster_id: roster.id,
      player_id: player_id,
    };
    console.log(payload);
    const endpoint = '/api/registry/teams/deleteInvite';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`Deleting invite failed: ${result['title']}`);
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
    const endpoint = '/api/registry/teams/kickPlayer';
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

  async function editNameTag(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    edit_dialog.close();
    const data = new FormData(event.currentTarget);
    const payload = {
      roster_id: roster.id,
      team_id: roster.team_id,
      name: data.get('name')?.toString(),
      tag: data.get('tag')?.toString(),
    };
    console.log(payload);
    const endpoint = '/api/registry/teams/requestRosterChange';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert(`Your request to change your roster's name/tag has been sent to MKCentral staff for approval.`);
    } else {
      alert(`Editing roster failed: ${result['title']}`);
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
      alert('Roster edited successfully');
    } else {
      alert(`Editing roster failed: ${result['title']}`);
    }
  }
</script>

<Section header="{roster.game} {roster.name}">
  <div slot="header_content">
    {#if roster.approval_status === 'approved'}
      <button on:click={edit_dialog.open}>Edit Roster</button>
    {/if}
  </div>
  {roster.players.length} player{roster.players.length !== 1 ? 's' : ''}
  {#if roster.players.length}
    <Table>
      <col class="country" />
      <col class="name" />
      <col class="fc" />
      <col class="join_date" />
      <col class="manage_player" />
      <thead>
        <tr>
          <th />
          <th>Name</th>
          <th>Friend Code</th>
          <th>Join Date</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {#each roster.players as player}
          <tr>
            <td>{player.country_code}</td>
            <td>{player.name}</td>
            <td>{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
            <td>{new Date(player.join_date * 1000).toLocaleString($locale, options)}</td>
            <td>
              <button on:click={() => kickDialog(player)}>Kick</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </Table>
  {/if}
  <br /><br />
  {#if roster.approval_status === 'approved'}
    <h3>Invitations</h3>
    {#if roster.invites.length}
      <Table>
        <col class="country" />
        <col class="name" />
        <col class="fc" />
        <col class="join_date" />
        <col class="manage_player" />
        <thead>
          <tr>
            <th />
            <th>Name</th>
            <th>Friend Code</th>
            <th>Join Date</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {#each roster.invites as player}
            <tr>
              <td>{player.country_code}</td>
              <td>{player.name}</td>
              <td>{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
              <td>{new Date(player.invite_date * 1000).toLocaleString($locale, options)}</td>
              <td>
                <button on:click={() => retractInvite(player.player_id)}>Retract Invite</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </Table>
    {/if}
    <br />
    <b>Invite Player</b>
    <br />
    <PlayerSearch bind:player={invite_player} game={roster.game} />
    {#if invite_player}
      <button on:click={() => invitePlayer(Number(invite_player?.id))}>Invite Player</button>
    {/if}
  {:else}
    Roster is pending approval from MKCentral staff.
  {/if}
</Section>

<Dialog bind:this={kick_dialog} header="Kick Player">
  Kick {curr_player?.name} from this roster?
  <div>
    <button on:click={() => kickPlayer(curr_player)}>Kick</button>
    <button on:click={kick_dialog.close}>Cancel</button>
  </div>
</Dialog>

<Dialog bind:this={edit_dialog} header="Edit Roster">
  <form method="post" on:submit|preventDefault={editNameTag}>
    <label for="name">Roster Name</label>
    <input name="name" type="text" value={roster.name} required />
    <br />
    <label for="tag">Roster Tag</label>
    <input name="tag" type="text" value={roster.tag} required />
    <br />
    <button type="submit">Request Name/Tag Change</button>
  </form>
  <br /><br />
  <form method="post" on:submit|preventDefault={editRoster}>
    <label for="recruiting">Recruitment Status</label>
    <select name="recruiting">
      <option value="true">Recruiting</option>
      <option value="false">Not Recruiting</option>
    </select>
    <br />
    <button type="submit">Edit Roster</button>
  </form>
</Dialog>