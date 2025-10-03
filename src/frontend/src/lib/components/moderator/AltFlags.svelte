<script lang="ts">
  import Table from '../common/Table.svelte';
  import LL from '$i18n/i18n-svelte';
  import type { AltFlag } from '$lib/types/alt-flag';
  import { page } from '$app/stores';
  import Flag from '../common/Flag.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import Button from '../common/buttons/Button.svelte';

  export let flags: AltFlag[];

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };

  // list of indexes which we should show flag data
  let show_details: Set<number> = new Set([]);

  function toggle_details(i: number) {
    if (show_details.has(i)) {
      show_details.delete(i);
    } else {
      show_details.add(i);
    }
    show_details = show_details;
  }

  function jsonToFieldString(jsonStr: string) {
    const obj = JSON.parse(jsonStr);
    return Object.entries(obj);
  }
</script>

{#if flags.length}
  <Table>
    <col class="players" />
    <col class="type" />
    <col class="score" />
    <col class="data mobile-hide" />
    <col class="date mobile-hide" />
    <thead>
      <tr>
        <th class="players">{$LL.MODERATOR.ALT_DETECTION.TABLE.PLAYERS()}</th>
        <th class="type">{$LL.MODERATOR.ALT_DETECTION.TABLE.TYPE()}</th>
        <th class="score">{$LL.MODERATOR.ALT_DETECTION.TABLE.SCORE()}</th>
        <th class="data mobile-hide">{$LL.MODERATOR.ALT_DETECTION.TABLE.DATA()}</th>
        <th class="date mobile-hide">{$LL.MODERATOR.ALT_DETECTION.TABLE.DETECTED_AT()}</th>
      </tr>
    </thead>
    <tbody>
      {#each flags as flag, i}
        <tr class="row-{i % 2}">
          <td class="players">
            {#each flag.users as user}
              {#if user.player}
                <a href="/{$page.params.lang}/registry/players/profile?id={user.player.id}">
                  <div class="player-name">
                    <Flag country_code={user.player.country_code} />
                    {user.player.name}
                  </div>
                </a>
              {:else}
                User ID {user.user_id}
              {/if}
            {/each}
          </td>
          <td class="type">
            {flag.type}
          </td>
          <td class="score">
            {flag.score}
          </td>
          <td class="data mobile-hide">
            {#if show_details.has(i)}
              <div>
                <Button on:click={() => toggle_details(i)}>{$LL.COMMON.HIDE()}</Button>
              </div>
              <div>
                {#each jsonToFieldString(flag.data) as entry}
                  <div>
                    {entry[0]}: {entry[1]}
                  </div>
                {/each}
              </div>
            {:else}
              <Button on:click={() => toggle_details(i)}>{$LL.COMMON.SHOW()}</Button>
            {/if}
          </td>
          <td class="date mobile-hide">
            {new Date(flag.date * 1000).toLocaleString($locale, options)}
          </td>
        </tr>
      {/each}
    </tbody>
  </Table>
{/if}

<style>
  col.players {
    width: 30%;
  }
  col.type {
    width: 20%;
  }
  col.score {
    width: 10%;
  }
  col.data {
    width: 20%;
  }
  col.date {
    width: 20%;
  }
  .player-name {
    display: flex;
    gap: 10px;
    align-items: center;
  }
</style>
