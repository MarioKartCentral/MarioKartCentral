<script lang="ts">
  import type { PlayerIPHistory } from '$lib/types/ip-addresses';
  import { locale } from '$i18n/i18n-svelte';
  import LL from '$i18n/i18n-svelte';
  import IpInfo from '$lib/components/moderator/IPInfo.svelte';

  export let history: PlayerIPHistory;

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };
</script>

{#each history.ips as p (p.id)}
  <IpInfo ip={p.ip_address} />
  <div class="history-container">
    <div>
      {new Date(p.date_earliest * 1000).toLocaleString($locale, options)}
      -
      {new Date(p.date_earliest * 1000).toLocaleString($locale, options)}
    </div>
    <div>
      {$LL.MODERATOR.ALT_DETECTION.NUM_TIMES({ count: p.times })}
    </div>
  </div>
{/each}

<style>
  .history-container {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
    background-color: rgba(255, 255, 255, 0.15);
    padding: 0px 10px;
    align-items: center;
    min-height: 45px;
  }
</style>
