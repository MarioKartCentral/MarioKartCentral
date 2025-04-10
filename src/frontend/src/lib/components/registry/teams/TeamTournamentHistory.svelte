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
  let podium_style: { [key: number]: string } = { 1: 'gold', 2: 'silver', 3: 'bronze' };

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
        return item.date_end <= Date.parse(String(to)) / 1000;
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
        <div class="flex flex-row flex-wrap items-center justify-center gap-2">
          <GameModeSelect bind:game bind:mode all_option hide_labels is_team inline/>
          <div class="flex flex-row flex-wrap items-center justify-center gap-2">
            <div class="flex flex-row items-center">
              <div class="w-12 mx-2">{$LL.COMMON.FROM()}</div>
              <input class="w-48" name="from" type="date" bind:value={from} />
            </div>
            <div class="flex flex-row items-center">
              <div class="w-12 mx-2">{$LL.COMMON.TO()}</div>
              <input class="w-48" name="to" type="date" bind:value={to} />
            </div>
          </div>
          <div class="ml-1 my-2">
            <Button type="submit">{$LL.COMMON.FILTER()}</Button>
          </div>
        </div>
      </form>
      <div>
        <Table>
          <thead>
            <tr>
              <th>{$LL.TOURNAMENTS.TOURNAMENT()}</th>
              <th class="mobile-hide">{$LL.TOURNAMENTS.HISTORY.TEAM()}</th>
              <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
              <th>{$LL.TOURNAMENTS.HISTORY.PLACEMENT()}</th>
            </tr>
          </thead>
          <tbody>
            {#each filtered_team_placements as placement, i}
              <tr class="{placement.placement && placement.placement <= 3 ? podium_style[placement.placement] : `row-${i % 2}`}">
                <td>
                  <a
                    href="/{$page.params.lang}/tournaments/details?id={placement.tournament_id}"
                  >
                    {placement.tournament_name}
                  </a>
                </td>
                {#if placement.team_id != null && placement.team_name != null}
                  <td class="mobile-hide">
                    <a
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
                    {$LL.TOURNAMENTS.HISTORY.DISQUALIFIED()}
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
    background-color: rgba(255, 254, 149, 0.30);
    color: #fffab0;
  }
  .silver {
    background-color: rgba(195, 255, 255, 0.3);
    color: #dcfffc;
  }
  .bronze {
    background-color: rgba(255, 158, 110, 0.30);
    color: #ffcbae;
  }
</style>
