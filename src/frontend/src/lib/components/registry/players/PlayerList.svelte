<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import Table from '$lib/components/common/Table.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';

  export let players: PlayerInfo[];
</script>

<Table>
  <col class="country_code" />
  <col class="name" />
  <col class="mk8dx"/>
  <col class="mkw"/>
  <col class="mkt"/>
  <col class="mk7"/>
  <col class="mk8"/>
  <thead>
    <tr>
      <th>Country Code</th>
      <th>Name</th>
      <th>Switch FC</th>
      <th>MKW FC</th>
      <th>MKT FC</th>
      <th>3DS FC</th>
      <th>NNID</th>
    </tr>
  </thead>
  <tbody>
    {#each players as player, i}
      <tr class="row-{i % 2}">
        <td>{player.country_code}</td>
        <td>
          <a href="/{$page.params.lang}/registry/players/profile?id={player.id}">{player.name}</a>
        </td>
        <td>{#if player.mk8dx}{player.mk8dx}{:else}-{/if}</td>
        <td>{#if player.mkw}{player.mkw}{:else}-{/if}</td>
        <td>{#if player.mkt}{player.mkt}{:else}-{/if}</td>
        <td>{#if player.mk7}{player.mk7}{:else}-{/if}</td>
        <td>{#if player.mk8}{player.mk8}{:else}-{/if}</td>
      </tr>
    {/each}
  </tbody>
</Table>

<style>
  col.country_code {
    width: 10%;
  }
  col.name {
    width: 20%;
  }
  col.mk8dx, col.mkw, col.mkt, col.mk7, col.mk8 {
    width: 10%
  } 
</style>
