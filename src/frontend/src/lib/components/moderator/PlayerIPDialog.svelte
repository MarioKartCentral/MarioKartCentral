<script lang="ts">
  import Dialog from '../common/Dialog.svelte';
  import type { PlayerIPHistory } from '$lib/types/ip-addresses';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import PlayerIpHistoryDisplay from '../registry/players/PlayerIPHistoryDisplay.svelte';

  export let player_id: number;
  let history: PlayerIPHistory;

  let ip_dialog: Dialog;
  export function open() {
    ip_dialog.open();
  }

  onMount(async () => {
    const res = await fetch(`/api/moderator/player_ips/${player_id}`);
    if (res.status === 200) {
      const body: PlayerIPHistory = await res.json();
      history = body;
    }
  });
</script>

<Dialog bind:this={ip_dialog} header={$LL.MODERATOR.ALT_DETECTION.PLAYER_IP_HISTORY()}>
  {#if history}
    <PlayerIpHistoryDisplay {history} />
  {/if}
</Dialog>
