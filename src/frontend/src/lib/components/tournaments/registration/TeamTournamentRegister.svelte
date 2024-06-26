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

  export let tournament: Tournament;
  export let player: PlayerInfo;

  let rosters: TeamRoster[] = [];

  let selected_roster: TeamRoster | null = null;
  let selected_rosters: TeamRoster[] = [];

  let captain_player: RosterPlayer | null = null;
  let selected_rep: RosterPlayer | null = null;
  let representatives: RosterPlayer[] = [];

  let squad_color = 1;

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

{#if check_registrations_open(tournament) && rosters.length}
<div class="container">


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
        <TagBadge tag={roster.tag} color={roster.color}/>
        {roster.name}
        {#if i === 0}
          <PrimaryBadge/>
          <!-- (Primary) -->
        {/if}
        <CancelButton on:click={() => removeRoster(roster)}/>
      </div>
    {/each}
    <div>
      <div>Squad Color</div>
      <ColorSelect tag={selected_rosters[0].tag} bind:color={squad_color}/>
    </div>
    {#if captain_player}
      <div><b>Captain:</b></div>
      <div>
          <Flag country_code={captain_player.country_code}/>
          {captain_player.name}
        {#if captain_player.player_id !== player.id}
          <CancelButton on:click={() => (captain_player = null)}/>
        {/if}
      </div>
      {#if representatives.length}
        <div>
          <b>Representatives</b>
        </div>
        {#each representatives as player}
          <div>
            <Flag country_code={captain_player.country_code}/>
            {player.name}
            <CancelButton on:click={() => removeRep(player)}/>
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
        <Button on:click={register}>Register</Button>
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
</div>
{/if}

<style>
  .container {
    margin: 20px 0;
  }
</style>