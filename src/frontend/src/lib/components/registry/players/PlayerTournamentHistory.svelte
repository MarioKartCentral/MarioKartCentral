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
  import SoloTournamentFields from '$lib/components/tournaments/registration/SoloTournamentFields.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export let player: PlayerInfo;

  let mode: string | null = null;
  let game: string | null = null;
  let from: string | null = null;
  let to: string | null = null;
  let player_placements: PlayerTournamentPlacement[] = [];
  let solo_placements: PlayerTournamentPlacement[] = [];
  let squad_placements: PlayerTournamentPlacement[] = [];
  let team_placements: PlayerTournamentPlacement[] = [];

  let avatar_url = logo;
  if (player.user_settings && player.user_settings.avatar) {
    avatar_url = player.user_settings.avatar;
  }

  async function fetchData() {
    let url = `/api/tournaments/players/placements/${player.id}`;
    // if (game !== null) {
    //   url += `&game=${game}`;
    // }
    // if (mode !== null) {
    //   url += `&mode=${mode}`;
    // }
    // if (from) {
    //   url += `&from_date=${new Date(from).getTime() / 1000}`;
    // }
    // if (to) {
    //   url += `&to_date=${new Date(to).getTime() / 1000}`;
    // }

    const res = await fetch(url);
    if (res.status !== 200) {
      return;
    }
    let body = await res.json();
    solo_placements = body.tournament_solo_placements;
    squad_placements = body.tournament_squad_placements;
    team_placements = body.tournament_team_placements;
  }

  onMount(fetchData);
  // console.log(player);
</script>

<Section header={$LL.PLAYER_TOURNAMENT_HISTORY.TOURNAMENT_HISTORY()}>
  <div>
    <div>
      <form on:submit|preventDefault={fetchData}>
        <div class="flex">
          <GameModeSelect bind:game bind:mode flex all_option hide_labels inline is_team />
          <Button type="submit">Filter</Button>
          <div class="option">
            <label for="from">From</label>
            <input name="from" type="datetime-local" bind:value={from} />
          </div>
          <div class="option">
            <label for="to">To</label>
            <input name="to" type="datetime-local" bind:value={to} />
          </div>
          <div class="option">
            <Button type="submit">Filter</Button>
          </div>
        </div>
      </form>
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
            {#each solo_placements as placement, i}
              <tr class="row-{i % 2}">
                <td> {placement.name} </td>
                <td> {placement.date_end}</td>
                {#if placement.partners != null}
                  <td>
                    {#each JSON.parse(placement.partners) as partner}
                      <!-- heyyy -->
                      <!-- {console.log('partner:' + partner.player_id + partner.name)} -->
                      <div class="flex flex-row">
                        <div class="hover:text-emerald-400">
                          <PlayerName player_id={partner.player_id} name={partner.name} />
                        </div>
                      </div>
                    {/each}
                  </td>
                {:else}
                  <td></td>
                {/if}
                <td> {placement.placement}</td>
              </tr>
            {/each}
          </tbody>
        </Table>
      </div>
    </div>
  </div></Section
>
