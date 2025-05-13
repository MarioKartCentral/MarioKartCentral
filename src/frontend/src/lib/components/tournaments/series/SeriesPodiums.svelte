<script lang="ts">
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import TypeBadge from '$lib/components/badges/TypeBadge.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { locale } from '$i18n/i18n-svelte';
  export let tournaments;

  const isPodium = (value) => value.placement <= 3;
  const comparePlacements = (a, b) => a.placement - b.placement;

  for (let i = 0; i < tournaments.length; i++) {
    tournaments[i].placements = tournaments[i].placements.filter(isPodium).sort(comparePlacements);
  }
  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
  };

  function getMedal(placement: number) {
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

  function getString(placement) {
    if (placement.squad.players.length > 4) {
      return placement.squad.name;
    }
    return placement.squad.players.map((player) => player.name).join(' / ');
  }

  function getColor(placement: number) {
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
      {#if tournaments[0]?.is_squad}
        {#each tournaments as tournament}
          {#if tournament.placements.length > 0}
            <tr>
              <td>
                <a href="/{$page.params.lang}/tournaments?id={tournament.id}">{tournament.name}</a>
              </td>
              <td class="right">
                {new Date(tournament.date_start * 1000).toLocaleString($locale, options)} - {new Date(
                  tournament.date_end * 1000,
                ).toLocaleDateString($locale, options)}
              </td>
            </tr>
            <tr>
              <td>
                <GameBadge game={tournament.game} />
                <ModeBadge mode={tournament.mode} />
                <TypeBadge is_squad={tournament.is_squad === 1} teams_allowed={tournament.teams_allowed === 1} />
              </td>
              <td class="right">
                {#each tournament.placements as placement}
                  {#if placement.placement < 4}
                    
                    <span class={getColor(placement.placement) + ' bold'}>
                      <a
                        href={`/${$page.params.lang}/tournaments/details?id=${tournament.id}`}
                      >
                        {'   ' + getMedal(placement.placement) + ' ' + getString(placement)}
                      </a>
                    </span>
                  {/if}
                {/each}
              </td>
            </tr>
          {/if}
        {/each}
      {:else}
        {#each tournaments as tournament}
          <tr>
            <td>
              <a href="/{$page.params.lang}/tournaments?id={tournament.id}">{tournament.name}</a>
            </td>
            <td class="right">
              {new Date(tournament.date_start * 1000).toLocaleDateString('fr-FR', options)} - {new Date(
                tournament.date_end * 1000,
              ).toLocaleDateString('fr-FR', options)}
            </td>
          </tr>
          <tr>
            <td>
              <GameBadge game={tournament.game} />
              <ModeBadge mode={tournament.mode} />
              <TypeBadge is_squad={tournament.is_squad === 1} teams_allowed={tournament.teams_allowed === 1} />
            </td>
            <td class="right">
              {#each tournament.placements as placement}
                <span class={getColor(placement.placement) + ' bold'}>
                  {#each placement.squad.players as player}
                    <a href={`/${$page.params.lang}/registry/players/profile?id=${player.player_id}`}>
                      {'   ' + getMedal(placement.placement) + ' ' + player.name}
                    </a>
                  {/each}
                </span>
              {/each}
            </td>
          </tr>
        {/each}
      {/if}
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
</style>
