<script lang="ts">
  import { Popover } from 'flowbite-svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import { page } from '$app/stores';
  import ArrowRight from '../../common/ArrowRight.svelte';
  import LL from '$i18n/i18n-svelte';

  export let player: PlayerInfo;

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
  };

  function unixTimestampToString(timestamp: number) {
    let date = new Date(timestamp * 1000);
    return date.toLocaleString($page.params.lang, options);
  }

  const sorted_changes = player.name_changes.filter((n) => n.approval_status === 'approved');
</script>

<Popover class="bg-gray-600 text-white">
  <div class="wrapper">
    <div class="history">
      {$LL.PLAYERS.PROFILE.NAME_CHANGE_HISTORY()}
    </div>
    {#each sorted_changes as change, i (change.id)}
      <div class="flex name-change">
        <div>
          {change.old_name}
        </div>
        <div class="flex">
          {#if i > 0}
            {unixTimestampToString(sorted_changes[i - 1].date)}
          {:else}
            {unixTimestampToString(player.join_date)}
          {/if}
          <ArrowRight />
          {unixTimestampToString(change.date)}
        </div>
      </div>
    {/each}
    <div class="flex name-change">
      <div>
        {player.name}
      </div>
      <div class="flex">
        {#if sorted_changes.length}
          {unixTimestampToString(sorted_changes[sorted_changes.length - 1].date)}
        {:else}
          {unixTimestampToString(player.join_date)}
        {/if}
        ~
      </div>
    </div>
  </div>
</Popover>

<style>
  div.wrapper {
    font-size: small;
  }
  div.history {
    font-weight: bold;
  }
  div.flex {
    display: flex;
    align-items: center;
  }
  div.name-change {
    gap: 5px;
  }
</style>
