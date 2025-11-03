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
  import { game_abbreviations } from '$lib/util/util';

  export let team: Team;

  let mode: string | null = null;
  let game: string | null = null;
  let from: string | null = null;
  let to: string | null = null;
  let roster_id: number | null = null;
  let team_placements: TeamTournamentPlacement[] = [];
  let filtered_team_placements: TeamTournamentPlacement[] = [];
  let podium_style: { [key: number]: string } = { 1: 'gold', 2: 'silver', 3: 'bronze' };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mode_strings: any = $LL.MODES;

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
    if (from) {
      filtered_team_placements = filtered_team_placements.filter((item) => {
        return item.date_end >= Date.parse(String(from)) / 1000;
      });
    }
    if (to) {
      filtered_team_placements = filtered_team_placements.filter((item) => {
        return item.date_end <= Date.parse(String(to)) / 1000;
      });
    }
    if (roster_id) {
      filtered_team_placements = filtered_team_placements.filter((item) =>
        item.rosters.some((r) => r.roster_id === roster_id),
      );
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
        <div class="flex flex-row flex-wrap items-center justify-center gap-2">
          <GameModeSelect bind:game bind:mode all_option hide_labels is_team inline />
          <div class="flex flex-row flex-wrap items-center justify-center gap-2">
            <div class="flex flex-row items-center">
              <div class="w-12 mx-2">{$LL.COMMON.FROM()}</div>
              <input class="w-48" name="from" type="date" bind:value={from} />
            </div>
            <div class="flex flex-row items-center">
              <div class="w-12 mx-2">{$LL.COMMON.TO()}</div>
              <input class="w-48" name="to" type="date" bind:value={to} />
            </div>
            <div class="flex flex-row items-center">
              <div class="w-12 mx-2">{$LL.TEAMS.PROFILE.ROSTER()}</div>
              <select bind:value={roster_id}>
                <option value={null}>{$LL.TEAMS.PROFILE.ALL_ROSTERS()}</option>
                {#each team.rosters as roster (roster.id)}
                  <option value={roster.id}>
                    {roster.name} ({game_abbreviations[roster.game]}
                    {mode_strings[roster.mode.toUpperCase()]()})
                  </option>
                {/each}
              </select>
            </div>
          </div>
          <div class="ml-1 my-2">
            <Button type="submit">{$LL.COMMON.FILTER()}</Button>
          </div>
        </div>
      </form>
      <div>
        <Table>
          <col class="tournament" />
          <col class="team mobile-hide" />
          <col class="date mobile-hide" />
          <col class="placement" />
          <thead>
            <tr>
              <th>{$LL.TOURNAMENTS.TOURNAMENT()}</th>
              <th class="mobile-hide">{$LL.TOURNAMENTS.HISTORY.TEAM()}</th>
              <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
              <th>{$LL.TOURNAMENTS.HISTORY.PLACEMENT()}</th>
            </tr>
          </thead>
          <tbody>
            {#each filtered_team_placements as placement, i (placement.registration_id)}
              <tr
                class={placement.placement && placement.placement <= 3
                  ? podium_style[placement.placement]
                  : `row-${i % 2}`}
              >
                <td>
                  <a href="/{$page.params.lang}/tournaments/details?id={placement.tournament_id}">
                    {placement.tournament_name}
                  </a>
                </td>
                <td class="mobile-hide">
                  <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">
                    {placement.squad_name}
                  </a>
                </td>

                <td class="mobile-hide">
                  {toDate(placement.date_start)}
                  {placement.date_end == placement.date_start ? '' : ' - ' + toDate(placement.date_end)}
                </td>
                <td>
                  {#if placement.is_disqualified}
                    {$LL.TOURNAMENTS.HISTORY.DISQUALIFIED()}
                  {:else}
                    {placement.placement ? $LL.COMMON.ORDINAL_SUFFIX({ val: placement.placement }) : '-'}
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
  col.tournament {
    width: 30%;
  }
  col.team {
    width: 30%;
  }
  col.date {
    width: 20%;
  }
  col.placement {
    width: 20%;
  }
  .gold {
    background-color: rgba(255, 254, 149, 0.3);
    color: #fffab0;
  }
  .silver {
    background-color: rgba(195, 255, 255, 0.3);
    color: #dcfffc;
  }
  .bronze {
    background-color: rgba(255, 158, 110, 0.3);
    color: #ffcbae;
  }
</style>
