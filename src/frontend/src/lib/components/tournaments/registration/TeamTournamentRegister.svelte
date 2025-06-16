<script lang="ts">
  import ColorSelect from '$lib/components/common/ColorSelect.svelte';
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
  import RosterSearch from '$lib/components/common/RosterSearch.svelte';
  import type { Team } from '$lib/types/team';
  import LL from '$i18n/i18n-svelte';

  export let tournament: Tournament;
  export let is_privileged = false;

  let rosters: TeamRoster[] = [];

  let selected_roster: TeamRoster | null = null;
  let selected_rosters: TeamRoster[] = [];

  let players: TeamTournamentPlayer[] = [];

  let squad_color = 1;
  let working = false;

  let selected_player: RosterPlayer | null = null;
  $: unselected_rosters = rosters.filter((r) => !selected_rosters.includes(r));

  $: all_players = selected_rosters.flatMap((r) => r.players);
  $: unselected_players = all_players.filter((p) => !players.some((p2) => p2.player_id === p.player_id));
  $: num_captains = players.filter((p) => p.is_captain).length;
  $: num_reps = players.filter((p) => p.is_captain || p.is_representative).length;
  $: can_register = ((!tournament.min_squad_size || num_captains === 1) && !(tournament.min_representatives && num_reps !== tournament.min_representatives) 
    && (!tournament.team_members_only || !tournament.min_squad_size || players.length >= tournament.min_squad_size) && (!tournament.max_squad_size || players.length <= tournament.max_squad_size));

  onMount(async () => {
    if(is_privileged) return; 
    const res = await fetch(
      `/api/registry/teams/getRegisterable?tournament_id=${tournament.id}&game=${tournament.game}&mode=${tournament.mode}`,
    );
    if (res.status < 300) {
      const body: TeamRoster[] = await res.json();
      rosters = body;
      console.log(rosters);
    }
  });

  async function selectRosterFromSearch(roster: TeamRoster | null) {
    selected_roster = null;
    if(!roster) return;
    if(selected_rosters.some((r) => r.id == roster.id)) return;

    // do an API request to get the players in the team
    const url = `/api/registry/teams/${roster.team_id}`;
    const res = await fetch(url);
    if(res.status !== 200) {
        alert(`Error ${res.status}`);
    }
    const body = await res.json();
    let team: Team = body;
    for(let r of team.rosters) {
        if(r.id === roster.id) {
            roster.players = r.players;
        }
    }
    selected_rosters.push(roster);
    for(let p of roster.players) {
        if(players.some((p2) => p2.player_id === p.player_id)) {
            continue;
        }
        players.push({...p, is_captain: p.is_manager, is_representative: false, is_bagger_clause: tournament.bagger_clause_enabled ? p.is_bagger_clause : false});
    }
    selected_rosters = selected_rosters;
    players = players;
  }

  function selectRosterFromList(roster: TeamRoster | null) {
    if (!roster) {
      return;
    }
    selected_rosters.push(roster);
    for(let p of roster.players) {
      // if player is already in our list don't add them
      if(players.some((p2) => p2.player_id === p.player_id)) {
        continue;
      }
      players.push({...p, is_captain: p.is_manager, is_representative: false, is_bagger_clause: tournament.bagger_clause_enabled ? p.is_bagger_clause : false});
    }
    // rosters = rosters;
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
    working = true;
    const payload = {
      squad_color: squad_color,
      squad_name: selected_rosters[0].name,
      squad_tag: selected_rosters[0].tag,
      roster_ids: selected_rosters.map((r) => r.id),
      players: players
    };
    const endpoint = `/api/tournaments/${tournament.id}/${is_privileged ? 'forceRegisterTeam' : 'registerTeam'}`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert($LL.TOURNAMENTS.REGISTRATIONS.REGISTER_TOURNAMENT_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.REGISTER_TOURNAMENT_FAILED()}: ${result['title']}`);
    }
  }

</script>

{#if is_privileged || (check_registrations_open(tournament) && rosters.length)}
  <div class="team_register">
    <div>
      <b>
        {is_privileged ? $LL.TOURNAMENTS.REGISTRATIONS.MANUALLY_REGISTER_TEAM() : $LL.TOURNAMENTS.REGISTRATIONS.REGISTER_TEAM()}
      </b>
    </div>
    {#if is_privileged}
      <RosterSearch bind:roster={selected_roster} game={tournament.game} mode={tournament.mode} is_active={is_privileged ? null : true}
      is_historical={null} on:change={() => selectRosterFromSearch(selected_roster)}/>
    {:else if unselected_rosters.length}
      <select bind:value={selected_roster} on:change={() => selectRosterFromList(selected_roster)}>
        <option value={null}>{$LL.TOURNAMENTS.REGISTRATIONS.SELECT_A_TEAM()}</option>
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
          <b>{$LL.TOURNAMENTS.REGISTRATIONS.SELECTED_ROSTERS()}</b>
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
        <div>{$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_COLOR_SELECT()}</div>
        <ColorSelect tag={selected_rosters[0].tag} bind:color={squad_color}/>
      </div>
      {#if players.length}
        <div class="section">
          <b>{$LL.TOURNAMENTS.REGISTRATIONS.SELECTED_PLAYERS()}</b>
          <Table>
            <col class="country"/>
            <col class="name"/>
            <col class="friend-codes mobile-hide" />
            <col class="actions"/>
            <thead>
              <tr>
                <th />
                <th>{$LL.COMMON.NAME()}</th>
                <th class="mobile-hide">{$LL.FRIEND_CODES.FRIEND_CODES()}</th>
                <th>{$LL.COMMON.ACTIONS()}</th>
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
                      <DropdownItem on:click={() => toggleCaptain(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.TOGGLE_CAPTAIN()}</DropdownItem>
                      {#if !player.is_captain}
                        <DropdownItem on:click={() => toggleRep(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.TOGGLE_REPRESENTATIVE()}</DropdownItem>
                      {/if}
                      {#if tournament.bagger_clause_enabled && !tournament.team_members_only}
                        <DropdownItem on:click={() => toggleBagger(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.TOGGLE_BAGGER()}</DropdownItem>
                      {/if}
                      <DropdownItem on:click={() => removePlayer(player)}>{$LL.TOURNAMENTS.REGISTRATIONS.REMOVE()}</DropdownItem>
                    </Dropdown>
                  </td>
                </tr>
              {/each}
            </tbody>
          </Table>
        </div>
      {/if}
      {#if unselected_players.length}
        <div class="section">
          <select bind:value={selected_player} on:change={() => addPlayer(selected_player)}>
            <option value={null} disabled>
              {$LL.TOURNAMENTS.REGISTRATIONS.ADD_PLAYER_SELECT()}
            </option>
            {#each unselected_players as player}
              <option value={player}>
                {player.name}
              </option>
            {/each}
          </select>
        </div>
      {/if}
      <div class="section">
        {#if tournament.min_squad_size && num_captains !== 1}
          <div>
            {$LL.TOURNAMENTS.REGISTRATIONS.SELECT_ONE_CAPTAIN()}
          </div>
        {/if}
        {#if tournament.min_representatives && num_reps !== tournament.min_representatives}
          <div>
            {$LL.TOURNAMENTS.REGISTRATIONS.SELECT_REPRESENTATIVES({min_representatives: tournament.min_representatives})}
          </div>
        {/if}
        {#if tournament.team_members_only && tournament.min_squad_size && players.length < tournament.min_squad_size}
          <div>
            {$LL.TOURNAMENTS.REGISTRATIONS.SELECT_MORE_PLAYERS({count: tournament.min_squad_size - players.length})}
          </div>
        {/if}
        {#if tournament.max_squad_size && players.length > tournament.max_squad_size}
          <div>
            {$LL.TOURNAMENTS.REGISTRATIONS.SELECT_LESS_PLAYERS({max_squad_size: tournament.max_squad_size, count: tournament.max_squad_size - players.length})}
          </div>
        {/if}
        <Button on:click={register} {working} disabled={!can_register}>{$LL.TOURNAMENTS.REGISTRATIONS.REGISTER()}</Button>
      </div>
    {/if}
  </div>
{/if}

<style>
  .section {
    margin: 15px 0;
  }
  .team_register {
    margin: 15px 0;
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