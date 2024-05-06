<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import Flag from '$lib/components/common/Flag.svelte';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  export let players: PlayerInfo[];
  export let currentPage: number;
  export let totalPages: number;
</script>

<PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages}/>

<Table>
  <col class="country_code" />
  <col class="name" />
  <col class="mk8dx mobile-hide" />
  <col class="mkw mobile-hide" />
  <col class="mkt mobile-hide" />
  <col class="mk7 mobile-hide" />
  <col class="mk8 mobile-hide" />
  <thead>
    <tr>
      <th></th>
      <th>{$LL.PLAYER_LIST.HEADER.NAME()}</th>
      <th class="mobile-hide">Switch FC</th>
      <th class="mobile-hide">MKW FC</th>
      <th class="mobile-hide">MKT FC</th>
      <th class="mobile-hide">3DS FC</th>
      <th class="mobile-hide">NNID</th>
    </tr>
  </thead>
  <tbody>
    {#each players as player, i}
      <tr class="row-{i % 2}">
        <td><Flag country_code={player.country_code} /></td>
        <td>
          <a href="/{$page.params.lang}/registry/players/profile?id={player.id}">{player.name}</a>
        </td>
        <td class="mobile-hide"
          >{#each player.friend_codes.filter((fc) => fc.game === "mk8dx") as friend_code}{friend_code.fc}{/each}</td
        >
        <td class="mobile-hide"
          >{#each player.friend_codes.filter((fc) => fc.game === "mkw") as friend_code}{friend_code.fc}{/each}</td
        >
        <td class="mobile-hide"
          >{#each player.friend_codes.filter((fc) => fc.game === "mkt") as friend_code}{friend_code.fc}{/each}</td
        >
        <td class="mobile-hide"
          >{#each player.friend_codes.filter((fc) => fc.game === "mk7") as friend_code}{friend_code.fc}{/each}</td
        >
        <td class="mobile-hide"
          >{#each player.friend_codes.filter((fc) => fc.game === "mk8") as friend_code}{friend_code.fc}{/each}</td
        >
      </tr>
    {/each}
  </tbody>
  
</Table>

<!-- <button on:click={() => (currentPage > 1 ? (currentPage = currentPage - 1) : (currentPage = currentPage))}
  >{'<'}</button
>
{currentPage}/{totalPages}
<button on:click={() => (currentPage < totalPages ? (currentPage = currentPage + 1) : (currentPage = currentPage))}
  >{'>'}</button
> -->

<style>
  col.country_code {
    width: 10%;
  }
  col.name {
    width: 15%;
  }
  col.mk8dx,
  col.mkw,
  col.mkt,
  col.mk7,
  col.mk8 {
    width: 15%;
  }
</style>
