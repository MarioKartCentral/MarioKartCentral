<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import TournamentInfo from '../TournamentInfo.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import TypeBadge from '$lib/components/badges/TypeBadge.svelte';
  export let tournaments: TournamentInfo[];
  let options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };

  function getMedail(placement: number) {
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

  function getColor(placement: number) {
    if (placement === 1) {
      return 'gold';
    }
    if (placement === 2) {
      return 'silver';
    }
    if (placement === 3) {
      return 'bronze';
    }
    return 'white';
  }
</script>

<Table>
  <col class="left" />
  <col class="right" />
  <tbody>
    {#if tournaments[0]?.is_squad}
      {#each tournaments as tournament}
        {#if tournament.placements.length > 0}
          <tr>
            <td>
              <a href="/{$page.params.lang}/tournaments?id={tournament.id}">{tournament.tournament_name}</a>
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
              <TypeBadge type={tournament.is_squad ? 'Squad' : 'Solo'} />
            </td>
            <td class="right">
              {#each tournament.placements as placement}
                {#if placement.placement < 3}
                  <span style="color:{getColor(placement.placement)}">
                    <a
                      href={`/${$page.params.lang}/tournaments/squads?id=${placement.squad.id}&tournament_id=${tournament.id}`}
                    >
                      {'   ' + getMedail(placement.placement) + ' ' + placement.squad.name}
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
            <a href="/{$page.params.lang}/tournaments?id={tournament.id}">{tournament.tournament_name}</a>
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
            <TypeBadge type={tournament.is_squad ? 'Squad' : 'Solo'} />
          </td>
          <td class="right">
            {#each tournament.placements as placement}
              <span style="color:{getColor(placement.placement)}">
                <a
                  href={`/${$page.params.lang}/registry/player?id=${placement.player.id}`}
                >
                  {'   ' + getMedail(placement.placement) + ' ' + placement.player.name}
                </a>
              </span>
            {/each}
          </td>
        </tr>
      {/each}
    {/if}
  </tbody>
</Table>

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
</style>
