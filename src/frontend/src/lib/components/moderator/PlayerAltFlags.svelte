<script lang="ts">
  import type { AltFlag } from '$lib/types/alt-flag';
  import Dialog from '../common/Dialog.svelte';
  import { onMount } from 'svelte';
  import AltFlags from './AltFlags.svelte';
  import LL from '$i18n/i18n-svelte';

  export let player_id: number;

  let alt_dialog: Dialog;
  let flags: AltFlag[] = [];
  let exclude_fingerprints = true;

  export function open() {
    alt_dialog.open();
  }

  async function fetchFlags() {
    const res = await fetch(
      `/api/moderator/playerAltFlags?player_id=${player_id}&exclude_fingerprints=${exclude_fingerprints}`,
    );
    if (res.status === 200) {
      const body: AltFlag[] = await res.json();
      console.log(body);
      flags = body;
    }
  }

  onMount(async () => {
    fetchFlags();
  });
</script>

<Dialog bind:this={alt_dialog} header={$LL.MODERATOR.ALT_DETECTION.PLAYER_ALT_FLAGS()}>
  <div>
    <select bind:value={exclude_fingerprints} on:change={fetchFlags}>
      <option value={true}>
        {$LL.MODERATOR.ALT_DETECTION.EXCLUDE_FINGERPRINTS()}
      </option>
      <option value={false}>
        {$LL.MODERATOR.ALT_DETECTION.INCLUDE_FINGERPRINTS()}
      </option>
    </select>
  </div>
  {#key flags}
    <AltFlags {flags} />
  {/key}
</Dialog>
