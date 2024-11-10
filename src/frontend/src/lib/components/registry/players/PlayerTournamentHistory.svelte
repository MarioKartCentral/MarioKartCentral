<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { UserInfo } from '$lib/types/user-info';
  import type { PlayerTournamentPlacement } from '$lib/types/tournament-placement';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import logo from '$lib/assets/logo.png';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import { game_order } from '$lib/util/util';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import PlayerName from '$lib/components/tournaments/registration/PlayerName.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export let player: PlayerInfo;

  let mode: string | null = null;
  let game: string | null = null;
  let from: string | null = null;
  let to: string | null = null;
  let solo_placements: PlayerTournamentPlacement[] = [];
  let team_placements: PlayerTournamentPlacement[] = [];
  let filtered_solo_placements: PlayerTournamentPlacement[] = [];
  let filtered_team_placements: PlayerTournamentPlacement[] = [];
  let podium_style: { [key: number]: string } = { 1: 'bg-amber-400/60', 2: 'bg-slate-400/60', 3: 'bg-amber-700/60' };

  let avatar_url = logo;
  if (player.user_settings && player.user_settings.avatar) {
    avatar_url = player.user_settings.avatar;
  }

  function toDate(unix_timestamp: number) {
    return new Date(unix_timestamp * 1000).toLocaleDateString();
  }

  async function applySort() {}

  async function fetchData() {
    // API
    let url = `/api/tournaments/players/placements/${player.id}`;
    const res = await fetch(url);
    if (res.status !== 200) {
      return;
    }
    let body = await res.json();
    team_placements = body.tournament_team_placements;
    solo_placements = body.tournament_solo_and_squad_placements;

    // Filtering
    filtered_team_placements = [...team_placements];
    filtered_solo_placements = [...solo_placements];

    if (game) {
      filtered_team_placements = filtered_team_placements.filter((item) => item.game === game);
      filtered_solo_placements = filtered_solo_placements.filter((item) => item.game === game);
    }
    if (mode) {
      filtered_team_placements = filtered_team_placements.filter((item) => item.mode === mode);
      filtered_solo_placements = filtered_solo_placements.filter((item) => item.mode === mode);
    }
    if (from) {
      filtered_solo_placements = filtered_solo_placements.filter((item) => {
        return item.date_start >= Date.parse(from) / 1000;
      });
    }
    if (to) {
      filtered_team_placements = filtered_team_placements.filter((item) => {
        return item.date_end <= Date.parse(to) / 1000;
      });
    }

    // Sorting
    filtered_solo_placements = filtered_solo_placements.sort((a, b) => {
      return b.date_start - a.date_start;
    });

    filtered_team_placements = filtered_team_placements.sort((a, b) => {
      return b.date_start - a.date_start;
    });
  }

  onMount(fetchData);
</script>

<Section header={$LL.PLAYER_TOURNAMENT_HISTORY.TOURNAMENT_HISTORY()}>
  <div>
    <form on:submit|preventDefault={fetchData}>
      <div class="filters flex">
        <GameModeSelect bind:game bind:mode flex all_option hide_labels inline is_team />
        <div class="filters flex">
          <div class="option">
            <input name="from" type="datetime-local" bind:value={from} />
          </div>
          <div class="text-xl font-bold mx-1">
            {'-'}
          </div>
          <div class="option">
            <input name="to" type="datetime-local" bind:value={to} />
          </div>
        </div>
      </div>
      <div class="option my-2">
        <Button type="submit">Filter</Button>
      </div>
    </form>
    <!-- Solo Tournaments -->
    <h2 class="text-2xl font-bold">Solo Tournaments</h2>
    <div>
      <Table>
        <thead>
          <tr>
            <th>Name</th>
            <th class="mobile-hide">Date</th>
            <th class="mobile-hide">Partners</th>
            <th>Placement</th>
          </tr>
        </thead>
        <tbody>
          {#each filtered_solo_placements as placement, i}
            <tr class={placement.placement ? podium_style[placement.placement] : `row-{i % 2}`}>
              <td>
                <a
                  class="hover:text-emerald-400"
                  href="/{$page.params.lang}/tournaments/details?id={placement.tournament_id}"
                >
                  {placement.tournament_name}
                </a>
              </td>
              <td class="mobile-hide">
                {toDate(placement.date_start)}
                {placement.date_end == placement.date_start ? '' : ' - ' + toDate(placement.date_end)}
              </td>
              {#if placement.partners != null}
                <td class="mobile-hide">
                  {#each placement.partners as partner}
                    <div class="flex flex-row">
                      <div class="hover:text-emerald-400">
                        <PlayerName player_id={partner.player_id} name={partner.player_name} />
                      </div>
                    </div>
                  {/each}
                </td>
              {:else}
                <td></td>
              {/if}
              <td>
                {placement.placement ? placement.placement : '-'}
                {placement.placement_description ? ' - ' + placement.placement_description : ''}
              </td>
            </tr>
          {/each}
        </tbody>
      </Table>
    </div>

    <!-- Team Tournaments -->
    <h2 class="text-2xl font-bold">Team Tournaments</h2>
    <div>
      <Table>
        <thead>
          <tr>
            <th>Name</th>
            <th class="mobile-hide">Date</th>
            <th class="mobile-hide">Team</th>
            <th>Placement</th>
          </tr>
        </thead>
        <tbody>
          {#each filtered_team_placements as placement, i}
            <tr class={placement.placement ? podium_style[placement.placement] : `row-{i % 2}`}>
              <td>
                <a
                  class="hover:text-emerald-400"
                  href="/{$page.params.lang}/tournaments/details?id={placement.tournament_id}"
                >
                  {placement.tournament_name}
                </a>
              </td>
              <td class="mobile-hide">
                {toDate(placement.date_start)}
                {placement.date_end == placement.date_start ? '' : ' - ' + toDate(placement.date_end)}
              </td>
              {#if placement.squad_id != null && placement.squad_name != null}
                <td class="mobile-hide">
                  <a
                    class="hover:text-emerald-400"
                    href="/{$page.params.lang}/registry/teams/profile?id={placement.team_id}"
                  >
                    {placement.squad_name}
                  </a>
                </td>
              {:else}
                <td></td>
              {/if}
              <td>
                {placement.placement ? placement.placement : '-'}
                {placement.placement_description ? ' - ' + placement.placement_description : ''}
              </td>
            </tr>
          {/each}
        </tbody>
      </Table>
    </div>
  </div>
</Section>

<style>
  @media screen and (max-width: 768px) {
    .filters {
      flex-direction: column;
    }
  }
</style>
