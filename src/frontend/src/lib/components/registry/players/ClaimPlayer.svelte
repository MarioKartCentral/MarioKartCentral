<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';

  export let player: PlayerInfo;
  let working = false;

  async function claimPlayer() {
    working = true;
    const payload = {
      player_id: player.id,
    };
    const endpoint = '/api/registry/players/claim';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      alert($LL.PLAYERS.SHADOW_PLAYERS.CLAIM_PLAYER_SUCCESS());
      window.location.reload();
    } else {
      alert(`${$LL.PLAYERS.SHADOW_PLAYERS.CLAIM_PLAYER_FAILED()}: ${result['title']}`);
    }
  }
</script>

<Section header={$LL.PLAYERS.SHADOW_PLAYERS.CLAIM_PLAYER()}>
  <div>
    {$LL.PLAYERS.SHADOW_PLAYERS.UNCLAIMED_PLAYER_DESCRIPTION()}
  </div>
  <div class="claim-button">
    <Button {working} on:click={claimPlayer}>{$LL.PLAYERS.SHADOW_PLAYERS.CLAIM_PLAYER()}</Button>
  </div>
</Section>

<style>
  .claim-button {
    margin-top: 10px;
  }
</style>
