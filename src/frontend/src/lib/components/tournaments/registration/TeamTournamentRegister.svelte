<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { RosterPlayer } from '$lib/types/roster-player';
  import type { TeamRoster } from '$lib/types/team-roster';
  import type { Tournament } from '$lib/types/tournament';
  import { onMount } from 'svelte';

  export let tournament: Tournament;
  export let player: PlayerInfo;

  let rosters: TeamRoster[] = [];

  let selected_roster: TeamRoster | null = null;
  let selected_rosters: TeamRoster[] = [];

  let captain_player: RosterPlayer | null = null;
  let selected_rep: RosterPlayer | null = null;
  let representatives: RosterPlayer[] = [];

  let squad_color: number = 1;

  $: unselected_rosters = rosters.filter((r) => !selected_rosters.includes(r));
  $: checkCaptain(selected_rosters);
  $: all_players = selected_rosters.flatMap((r) => r.players);
  $: unselected_players = all_players.filter((p) => !representatives.includes(p) && p !== captain_player);

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
    rosters = rosters;
    selected_rosters = selected_rosters;
    selected_roster = null;
  }

  function removeRoster(roster: TeamRoster) {
    selected_rosters = selected_rosters.filter((r) => r.id !== roster.id);
  }

  function checkRosters(rosters: TeamRoster[], player_id: number) {
    // set captain player to passed-in player if they exist
    for (let roster of rosters) {
      for (let roster_player of roster.players) {
        if (player_id === roster_player.player_id) {
          captain_player = roster_player;
          if (representatives.includes(captain_player)) {
            removeRep(captain_player);
          }
          return true;
        }
      }
    }
    return false;
  }

  function checkCaptain(rosters: TeamRoster[]) {
    // check if logged-in user is in any rosters
    if (checkRosters(rosters, player.id)) {
      return;
    }
    // if we've selected an alternative captain, make sure they're in any rosters too
    if (captain_player && checkRosters(rosters, captain_player.player_id)) {
      return;
    }
    // if neither we or the player we selected are in any selected rosters,
    // set captain player to null so we have to select again
    captain_player = null;
  }

  function selectRep(player: RosterPlayer | null) {
    if (!player) {
      return;
    }
    representatives.push(player);
    representatives = representatives;
    selected_rep = null;
  }

  function removeRep(player: RosterPlayer) {
    representatives = representatives.filter((r) => r.player_id !== player.player_id);
  }

  async function register() {
    const payload = {
      squad_color: squad_color,
      squad_name: selected_rosters[0].name,
      squad_tag: selected_rosters[0].tag,
      captain_player: captain_player?.player_id,
      roster_ids: selected_rosters.map((r) => r.id),
      representative_ids: representatives.map((r) => r.player_id),
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

{#if rosters.length}
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
    <div>
      <b>Selected Rosters:</b>
    </div>
    {#each selected_rosters as roster, i}
      <div>
        {roster.name}
        {#if i === 0}
          (Primary)
        {/if}
        <button on:click={() => removeRoster(roster)}>X</button>
      </div>
    {/each}
    <div>
      <div>Squad Color</div>
      <input type="number" min="1" bind:value={squad_color} />
    </div>
    {#if captain_player}
      <div><b>Captain:</b></div>
      <div>
        {captain_player.name}
        {#if captain_player.player_id !== player.id}
          <button on:click={() => (captain_player = null)}> X </button>
        {/if}
      </div>
      {#if representatives.length}
        <div>
          <b>Representatives</b>
        </div>
        {#each representatives as player}
          <div>
            {player.name}
            <button on:click={() => removeRep(player)}> X </button>
          </div>
        {/each}
      {/if}
      {#if tournament.min_representatives && representatives.length + 1 < tournament.min_representatives}
        <div>
          <b>Select {tournament.min_representatives - representatives.length - 1} more representatives</b>
        </div>
        <select bind:value={selected_rep} on:change={() => selectRep(selected_rep)}>
          {#each unselected_players as player}
            <option value={player}>
              {player.name}
            </option>
          {/each}
        </select>
      {:else}
        <button on:click={register}>Register</button>
      {/if}
    {:else}
      <div>Select captain</div>
      <div>
        <select bind:value={captain_player}>
          {#each all_players as player}
            <option value={player}>{player.name}</option>
          {/each}
        </select>
      </div>
    {/if}
  {/if}
{/if}
