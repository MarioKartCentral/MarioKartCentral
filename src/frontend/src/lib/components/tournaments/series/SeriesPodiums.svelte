<script lang="ts">
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import TypeBadge from '$lib/components/badges/TypeBadge.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import type { TournamentWithPlacements } from '$lib/types/tournament';
  import type { TournamentPlacement } from '$lib/types/tournament-placement';

  export let tournaments: TournamentWithPlacements[];

  const isPodium = (value: TournamentPlacement) => value.placement && value.placement <= 3;
  const comparePlacements = (a: TournamentPlacement, b: TournamentPlacement) => {
    if (a.placement === null) {
      if (b.placement !== null) {
        return 1;
      } else {
        return 0;
      }
    }
    if (b.placement === null) {
      return -1;
    }
    return a.placement - b.placement;
  };

  for (let i = 0; i < tournaments.length; i++) {
    tournaments[i].placements = tournaments[i].placements.filter(isPodium).sort(comparePlacements);
  }

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
  };

  function getMedal(placement: number | null) {
    if (placement === 1) {
      return '👑';
    }
    if (placement === 2) {
      return '🥈';
    }
    if (placement === 3) {
      return '🥉';
    }
    return '🐢';
  }

  function getColor(placement: number | null) {
    if (placement === 1) {
      return 'gold_color';
    }
    if (placement === 2) {
      return 'silver_color';
    }
    if (placement === 3) {
      return 'brown_color';
    }
    return 'white';
  }
</script>

<Section header="Tournament History">
  <Table>
    <col class="left" />
    <col class="right" />
    <tbody>
      {#each tournaments as t, i (t.id)}
        <tr class="row-{i % 2}">
          <td class="left">
            <div class="row_top tournament_name">
              <a href="/{$page.params.lang}/tournaments/details?id={t.id}">{t.name}</a>
            </div>
            <div>
              <GameBadge game={t.game} />
              <ModeBadge mode={t.mode} />
              <TypeBadge is_squad={t.is_squad} teams_allowed={t.teams_allowed} />
            </div>
          </td>
          <td class="right">
            <div class="row_top">
              {new Date(t.date_start * 1000).toLocaleDateString($locale, options)} - {new Date(
                t.date_end * 1000,
              ).toLocaleDateString($locale, options)}
            </div>
            <div>
              {#each t.placements as p (p.registration_id)}
                <span class={getColor(p.placement) + ' bold'}>
                  {getMedal(p.placement)}
                  {#if p.squad.rosters.length}
                    <a href={`/${$page.params.lang}/registry/teams/profile?id=${p.squad.rosters[0].team_id}`}>
                      {p.squad.rosters[0].team_name}
                    </a>
                  {:else if p.squad.name}
                    <a href="/{$page.params.lang}/tournaments/details?id={t.id}">
                      {p.squad.name}
                    </a>
                  {:else}
                    {#each p.squad.players as player, i (player.id)}
                      {#if i < 4}
                        <a href={`/${$page.params.lang}/registry/players/profile?id=${player.player_id}`}>
                          {player.name}
                        </a>
                        {#if player !== p.squad.players[p.squad.players.length - 1]}
                          <span class="white_color">
                            {' / '}
                          </span>
                        {/if}
                      {/if}
                      {#if i === 4}
                        <span class="white_color">{' ...'}</span>
                      {/if}
                    {/each}
                  {/if}
                </span>
              {/each}
            </div>
          </td>
        </tr>
      {/each}
    </tbody>
  </Table>
</Section>

<style>
  col.left {
    width: 50%;
  }
  col.right {
    width: 50%;
  }
  .right {
    text-align: right;
  }

  .bold {
    font-weight: bold;
  }

  .gold_color {
    color: #e1c15e;
  }

  .silver_color {
    color: #b8cde1;
  }

  .brown_color {
    color: #d17f26;
  }

  .row_top {
    margin-bottom: 10px;
  }

  .white_color {
    color: white;
  }

  .tournament_name {
    font-size: 1.125rem;
  }
</style>
