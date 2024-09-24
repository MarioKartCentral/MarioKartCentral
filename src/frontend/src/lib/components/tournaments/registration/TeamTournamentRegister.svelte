<script lang="ts">
  import ColorSelect from '$lib/components/common/ColorSelect.svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { RosterPlayer } from '$lib/types/roster-player';
  import type { TeamRoster } from '$lib/types/team-roster';
  import type { Tournament } from '$lib/types/tournament';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { onMount } from 'svelte';
  import { check_registrations_open } from '$lib/util/util';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import PrimaryBadge from '$lib/components/badges/PrimaryBadge.svelte';
  import type { TeamTournamentPlayer } from '$lib/types/team-tournament-player';
  import Table from '$lib/components/common/Table.svelte';
  import FriendCodeDisplay from '$lib/components/common/FriendCodeDisplay.svelte';
  import { ChevronDownSolid } from 'flowbite-svelte-icons';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import PlayerName from './PlayerName.svelte';

  export let tournament: Tournament;
  export let user_player: PlayerInfo;

  let rosters: TeamRoster[] = [];

  let selected_roster: TeamRoster | null = null;
  let selected_rosters: TeamRoster[] = [];

  let players: TeamTournamentPlayer[] = [];

  let squad_color = 1;

  let selected_player: RosterPlayer | null = null;
  $: unselected_rosters = rosters.filter((r) => !selected_rosters.includes(r));

  $: all_players = selected_rosters.flatMap((r) => r.players);
  $: unselected_players = all_players.filter((p) => !players.some((p2) => p2.player_id === p.player_id));
  $: num_captains = players.filter((p) => p.is_captain).length;
  $: num_reps = players.filter((p) => p.is_captain || p.is_representative).length;
  $: can_register = (num_captains === 1 && !(tournament.min_representatives && num_reps !== tournament.min_representatives) 
    && (!tournament.min_squad_size || players.length >= tournament.min_squad_size) && (!tournament.max_squad_size || players.length <= tournament.max_squad_size));

  onMount(async () => {
    const res = await fetch(
      `/api/registry/teams/getRegisterable?tournament_id=${tournament.id}&game=${tournament.game}&mode=${tournament.mode}`,
    );
    if (res.status < 300) {
      const body: TeamRoster[] = await res.json();
      rosters = body;
      console.log(rosters);
    }
  });

  function selectRoster(roster: TeamRoster | null) {
    if (!roster) {
      return;
    }
    selected_rosters.push(roster);
    for(let p of roster.players) {
      // if player is already in our list don't add them
      if(players.some((p2) => p2.player_id === p.player_id)) {
        continue;
      }
      players.push({...p, is_captain: p.player_id === user_player.id, is_representative: false, is_bagger_clause: tournament.bagger_clause_enabled ? p.is_bagger_clause : false});
    }
    rosters = rosters;
    players = players;
    selected_rosters = selected_rosters;
    selected_roster = null;
  }

  function removeRoster(roster: TeamRoster) {
    selected_rosters = selected_rosters.filter((r) => r.id !== roster.id);
    // remove any players which are not in a selected roster from our players array
    let selected_players = selected_rosters.flatMap((r) => r.players);
    players = players.filter((p) => selected_players.some((p2) => p.player_id === p2.player_id));
  }

  function toggleCaptain(player: TeamTournamentPlayer) {
    if(player.is_captain) {
      player.is_captain = false;
      players = players;
      return;
    }
    for(let p of players) {
      p.is_captain = false;
    }
    player.is_captain = true;
    player.is_representative = false;
    players = players;
  }

  function toggleRep(player: TeamTournamentPlayer) {
    player.is_representative = !player.is_representative;
    player.is_captain = false;
    players = players;
  }

  function toggleBagger(player: TeamTournamentPlayer) {
    player.is_bagger_clause = !player.is_bagger_clause;
    players = players;
  }

  function removePlayer(player: TeamTournamentPlayer) {
    players = players.filter((p) => p.player_id !== player.player_id);
  }

  function addPlayer(player: RosterPlayer | null) {
    if(!player) return;
    if(!players.some((p) => p.player_id === player.player_id)) {
      players.push({...player, is_captain: false, is_representative: false, is_bagger_clause: tournament.bagger_clause_enabled ? player.is_bagger_clause : false});
    }
    selected_player = null;
    players = players;
  }

  async function register() {
    const payload = {
      squad_color: squad_color,
      squad_name: selected_rosters[0].name,
      squad_tag: selected_rosters[0].tag,
      roster_ids: selected_rosters.map((r) => r.id),
      players: players
    };
    const endpoint = `/api/tournaments/${tournament.id}/registerTeam`;
    console.log(payload);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert('Successfully registered for the tournament!');
    } else {
      alert(`Registration failed: ${result['title']}`);
    }
  }

</script>

{#if check_registrations_open(tournament) && rosters.length}
<div class="team_register">
  <div>
    <b>Register Team</b>
  </div>
  {#if unselected_rosters.length}
    <select bind:value={selected_roster} on:change={() => selectRoster(selected_roster)}>
      <option value={null}>Select a team</option>
      {#each unselected_rosters as roster}
        <option value={roster}>
          {roster.name}
        </option>
      {/each}
    </select>
  {/if}
  {#if selected_rosters.length}
    <div class="section">
      <div>
        <b>Selected Rosters:</b>
      </div>
      {#each selected_rosters as roster, i}
        <div>
          <TagBadge tag={roster.tag} color={roster.color}/>
          {roster.name}
          {#if i === 0}
            <PrimaryBadge/>
          {/if}
          <CancelButton on:click={() => removeRoster(roster)}/>
        </div>
      {/each}
    </div>
    <div class="section">
      <div>Squad Color</div>
      <ColorSelect tag={selected_rosters[0].tag} bind:color={squad_color}/>
    </div>
    <div class="section">
      <b>Players:</b>
      <Table>
        <col class="country"/>
        <col class="name"/>
        <col class="friend-codes mobile-hide" />
        <col class="actions"/>
        <thead>
          <tr>
            <th />
            <th>Name</th>
            <th class="mobile-hide">Friend Codes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each players as player, i}
            <tr class="row-{i % 2}">
              <td>
                <Flag country_code={player.country_code}/>
              </td>
              <td>
                <PlayerName player_id={player.player_id} name={player.name} is_squad_captain={player.is_captain}
                is_representative={player.is_representative} is_bagger_clause={player.is_bagger_clause}/>
              </td>
              <td class="mobile-hide">
                <FriendCodeDisplay friend_codes={player.friend_codes}/>
              </td>
              <td>
                <ChevronDownSolid class="cursor-pointer"/>
                <Dropdown>
                  <DropdownItem on:click={() => toggleCaptain(player)}>Toggle Captain</DropdownItem>
                  {#if !player.is_captain}
                    <DropdownItem on:click={() => toggleRep(player)}>Toggle Representative</DropdownItem>
                  {/if}
                  {#if tournament.bagger_clause_enabled && !tournament.team_members_only}
                    <DropdownItem on:click={() => toggleBagger(player)}>Toggle Bagger</DropdownItem>
                  {/if}
                  <DropdownItem on:click={() => removePlayer(player)}>Remove</DropdownItem>
                </Dropdown>
              </td>
            </tr>
          {/each}
        </tbody>
      </Table>
    </div>
    {#if unselected_players.length}
      <div class="section">
        <select bind:value={selected_player} on:change={() => addPlayer(selected_player)}>
          {#each unselected_players as player}
            <option value={player}>
              {player.name}
            </option>
          {/each}
        </select>
      </div>
    {/if}
    <div class="section">
      {#if num_captains !== 1}
        <div>
          Please select exactly one captain
        </div>
      {/if}
      {#if tournament.min_representatives && num_reps !== tournament.min_representatives}
        <div>
          Please select exactly {tournament.min_representatives} captains/representatives
        </div>
      {/if}
      {#if tournament.min_squad_size && players.length < tournament.min_squad_size}
        <div>
          Please add {tournament.min_squad_size - players.length} more players
        </div>
      {/if}
      {#if tournament.max_squad_size && players.length > tournament.max_squad_size}
        <div>
          This tournament's max squad size is {tournament.max_squad_size}, please remove at least {tournament.max_squad_size - players.length} players
        </div>
      {/if}
      <Button on:click={register} disabled={!can_register}>Register</Button>
    </div>
  {/if}
</div>
{/if}

<style>
  .section {
    margin: 15px 0;
  }
  .team_register {
    margin-bottom: 15px;
  }
  col.country {
    width: 15%;
  }
  col.name {
    width: 35%;
  }
  col.friend-codes {
    width: 30%;
  }
  col.actions {
    width: 20%;
  }
</style>