<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';

  export let players: PlayerInfo[];
  export let currentPage: number;
  export let totalPages: number;
</script>

<Table>
  <col class="country_code" />
  <col class="name" />
  <col class="mk8dx" />
  <col class="mkw" />
  <col class="mkt" />
  <col class="mk7" />
  <col class="mk8" />
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
        <td
          >{#each player.friend_codes as friend_code}{#if friend_code.game == 'mk8dx'}{friend_code.fc}{/if}{/each}</td
        >
        <td
          >{#each player.friend_codes as friend_code}{#if friend_code.game == 'mkw'}{friend_code.fc}{/if}{/each}</td
        >
        <td
          >{#each player.friend_codes as friend_code}{#if friend_code.game == 'mkt'}{friend_code.fc}{/if}{/each}</td
        >
        <td
          >{#each player.friend_codes as friend_code}{#if friend_code.game == 'mk7'}{friend_code.fc}{/if}{/each}</td
        >
        <td
          >{#each player.friend_codes as friend_code}{#if friend_code.game == 'mk8'}{friend_code.fc}{/if}{/each}</td
        >
      </tr>
    {/each}
  </tbody>
  <button on:click={() => (currentPage > 1 ? (currentPage = currentPage - 1) : (currentPage = currentPage))}
    >{'<'}</button
  >
  {currentPage}/{totalPages}
  <button on:click={() => (currentPage < totalPages ? (currentPage = currentPage + 1) : (currentPage = currentPage))}
    >{'>'}</button
  >
</Table>

<style>
  col.country_code {
    width: 10%;
  }
  col.name {
    width: 20%;
  }
  col.mk8dx,
  col.mkw,
  col.mkt,
  col.mk7,
  col.mk8 {
    width: 10%;
  }
</style>
