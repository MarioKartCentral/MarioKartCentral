<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import type { Team } from '$lib/types/team';
  import type { TeamTournamentPlacement } from '$lib/types/tournament-placement';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';

  export let team: Team;

  let mode: string | null = null;
  let game: string | null = null;
  let from: string | null = null;
  let to: string | null = null;
  let team_placements: TeamTournamentPlacement[] = [];
  let filtered_team_placements: TeamTournamentPlacement[] = [];
  // Default 'silver' from PlacementsDisplay.svelte is less readable than I'd like
  let podium_style: { [key: number]: string } = { 1: 'gold', 2: 'bg-slate-400/60', 3: 'bronze' };

  function toDate(unix_timestamp: number) {
    return new Date(unix_timestamp * 1000).toLocaleDateString();
  }

  async function fetchData() {
    // API
    let url = `/api/tournaments/teams/placements/${team.id}`;
    const res = await fetch(url);
    if (res.status !== 200) {
      return;
    }
    let body = await res.json();
    team_placements = body.tournament_team_placements;
    // No need to filter if there is no data
    if (team_placements.length == 0) {
      return;
    }
    filterData();
  }

  function filterData() {
    // Filtering
    filtered_team_placements = [...team_placements];

    if (game) {
      filtered_team_placements = filtered_team_placements.filter((item) => item.game === game);
    }
    if (mode) {
      filtered_team_placements = filtered_team_placements.filter((item) => item.mode === mode);
    }
    if (to) {
      filtered_team_placements = filtered_team_placements.filter((item) => {
        return item.date_end <= Date.parse(to) / 1000;
      });
    }

    filtered_team_placements = filtered_team_placements.sort((a, b) => {
      return b.date_start - a.date_start;
    });
  }

  onMount(fetchData);
</script>

<!-- Dont render component if API response is empty  -->
{#if team_placements.length != 0}
  <Section header={$LL.TOURNAMENTS.HISTORY.TOURNAMENT_HISTORY()}>
    <div class="w-full m-auto">
      <form on:submit|preventDefault={filterData}>
        <div class="flex flex-row flex-wrap items-center justify-center">
          <GameModeSelect bind:game bind:mode all_option hide_labels is_team />
          <div class="flex flex-col">
            <div class="ml-1">
              <input class="w-44" name="from" type="date" bind:value={from} />
            </div>
            <div class="ml-1">
              <input class="w-44" name="to" type="date" bind:value={to} />
            </div>
          </div>
          <div class="ml-1 my-2">
            <Button type="submit">Filter</Button>
          </div>
        </div>
      </form>

      <!-- Team Tournaments -->
      <!-- <h2 class="text-2xl font-bold">{$LL.TOURNAMENTS.HISTORY.TEAM_TOURNAMENTS()}</h2> -->
      <div>
        <Table>
          <thead>
            <tr>
              <th>Tournament</th>
              <th class="mobile-hide">Team</th>
              <th class="mobile-hide">Date</th>
              <th>Placement</th>
            </tr>
          </thead>
          <tbody>
            {#each filtered_team_placements as placement, i}
              <tr class="row-{i % 2} {placement.placement ? podium_style[placement.placement] : ''}">
                <td>
                  <a
                    class="hover:text-emerald-400"
                    href="/{$page.params.lang}/tournaments/details?id={placement.tournament_id}"
                  >
                    {placement.tournament_name}
                  </a>
                </td>
                {#if placement.team_id != null && placement.team_name != null}
                  <td class="mobile-hide">
                    <a
                      class="hover:text-emerald-400"
                      href="/{$page.params.lang}/registry/teams/profile?id={placement.team_id}"
                    >
                      {placement.team_name}
                    </a>
                  </td>
                {:else}
                  <td></td>
                {/if}
                <td class="mobile-hide">
                  {toDate(placement.date_start)}
                  {placement.date_end == placement.date_start ? '' : ' - ' + toDate(placement.date_end)}
                </td>
                <td>
                  {#if placement.is_disqualified}
                    Disqualified
                  {:else}
                    {placement.placement ? $LL.COMMON.ORDINAL_SUFFIX({val: placement.placement}) : '-'}
                    {placement.placement_description ? ' - ' + placement.placement_description : ''}
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </Table>
      </div>
    </div>
  </Section>
{/if}

<style>
  .gold {
    background-color: rgba(250, 209, 5, 0.6);
  }
  .silver {
    background-color: rgba(255, 255, 255, 0.5);
  }
  .bronze {
    background-color: rgba(255, 136, 0, 0.5);
  }
</style>
