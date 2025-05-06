<script lang="ts">
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { sortByMedals, sortByAppearances } from '$lib/util/series_stats';
  export let stats;
  let stats_mode = 'team_medals';
  stats.rostersArray = sortByMedals(stats.rostersArray);

  function handleTeamMedalsClick() {
    stats_mode = 'team_medals';
    stats.rostersArray = sortByMedals(stats.rostersArray);
  }

  function handleTeamAppearancesClick() {
    stats_mode = 'team_appearances';
    stats.rostersArray = sortByAppearances(stats.rostersArray);
  }

  function handlePlayerMedalsClick() {
    stats_mode = 'player_medals';
    stats.playersArray = sortByMedals(stats.playersArray);
  }

  function handlePlayerAppearancesClick() {
    stats_mode = 'player_appearances';
    stats.playersArray = sortByAppearances(stats.playersArray);
  }
</script>

<Section header="Stats">
  <div style="background-color: darkcyan;">
    Teams :
    <Button type="submit" on:click={() => handleTeamMedalsClick()}>Podium Finishes</Button>
    <Button type="submit" on:click={() => handleTeamAppearancesClick()}>Tournament Appearances</Button>
  </div>
  <div style="background-color: darkblue;">
    Players :
    <Button on:click={() => handlePlayerMedalsClick()}>Podium Finishes</Button>
    <Button on:click={() => handlePlayerAppearancesClick()}>Tournament Appearances</Button>
  </div>

  {#if stats_mode === 'team_medals'}
    <Table>
      <col class="placement" />
      <col class="team_tag" />
      <col class="team_name" />
      <col class="gold" />
      <col class="silver" />
      <col class="bronze" />
      <thead><tr><th></th><th></th><th></th><th>👑</th><th>🥈</th><th>🥉</th></tr></thead>
      {#each stats.rostersArray as roster}
        <tr>
          <td>{roster.medals_placement}</td>
          <td><TagBadge tag={roster.tag} color={1} /></td>
          <td>{roster.name}</td>
          <td>{roster.gold > 0 ? roster.gold : '-'}</td>
          <td>{roster.silver > 0 ? roster.silver : '-'}</td>
          <td>{roster.bronze > 0 ? roster.bronze : '-'}</td>
        </tr>
      {/each}
    </Table>
  {/if}
  {#if stats_mode === 'team_appearances'}
    <Table>
      <col class="placement" />
      <col class="team_tag" />
      <col class="team_name" />
      <col class="appearances" />
      <thead><tr><th></th><th></th><th></th><th>Appearances</th></tr></thead>
      {#each stats.rostersArray as roster}
        <tr>
          <td>{roster.appearances_placement}</td>
          <td><TagBadge tag={roster.tag} color={1} /></td>
          <td>{roster.name}</td>
          <td>{roster.appearances}</td>
        </tr>
      {/each}
    </Table>
  {/if}
  {#if stats_mode === 'player_medals'}
    <Table>
      <col class="placement" />
      <col class="team_tag" />
      <col class="team_name" />
      <col class="gold" />
      <col class="silver" />
      <col class="bronze" />
      <thead><tr><th></th><th></th><th></th><th>👑</th><th>🥈</th><th>🥉</th></tr></thead>
      {#each stats.playersArray as player}
        <tr>
          <td>{player.medals_placement}</td>
          <td>{player.country_code}</td>
          <td>{player.name}</td>
          <td>{player.gold > 0 ? player.gold : '-'}</td>
          <td>{player.silver > 0 ? player.silver : '-'}</td>
          <td>{player.bronze > 0 ? player.bronze : '-'}</td>
        </tr>
      {/each}
    </Table>
  {/if}
  {#if stats_mode === 'player_appearances'}
    <Table>
      <col class="placement" />
      <col class="team_tag" />
      <col class="team_name" />
      <col class="appearances" />
      <thead><tr><th></th><th></th><th></th><th>Appearances</th></tr></thead>
      {#each stats.playersArray as player}
        <tr>
          <td>{player.appearances_placement}</td>
          <td>{player.country_code}</td>
          <td>{player.name}</td>
          <td>{player.appearances}</td>
        </tr>
      {/each}
    </Table>
  {/if}
</Section>

<style></style>
