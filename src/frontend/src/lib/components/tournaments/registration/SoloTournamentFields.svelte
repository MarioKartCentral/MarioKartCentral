<script lang="ts">
  import type { FriendCode } from '$lib/types/friend-code';
  import type { Tournament } from '$lib/types/tournament';

  export let tournament: Tournament;
  export let friend_codes: FriendCode[];
  export let selected_fc_id: number | null = null;
  export let mii_name: string | null = null;
  export let can_host = false;
</script>

{#if tournament.require_single_fc}
  <div>
    <label for="selected_fc_id">Select FC</label>
    <select name="selected_fc_id" value={selected_fc_id} required>
      {#each friend_codes as fc}
        <option value={fc.id}>{fc.fc}</option>
      {/each}
    </select>
  </div>
{/if}
{#if tournament.mii_name_required}
  <div>
    <label for="mii_name">In-game/Mii Name</label>
    <input name="mii_name" maxlength={tournament.game === 'mkt' ? 12 : 10} value={mii_name} required />
  </div>
{/if}
{#if tournament.host_status_required}
  <div>
    <label for="can_host">Can host?</label>
    <select name="can_host" value={Boolean(can_host)} required>
      <option value={false}>No</option>
      <option value={true}>Yes</option>
    </select>
  </div>
{/if}
