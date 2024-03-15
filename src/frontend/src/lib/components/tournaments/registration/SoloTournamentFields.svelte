<script lang="ts">
  import type { FriendCode } from '$lib/types/friend-code';
  import type { Tournament } from '$lib/types/tournament';

  export let tournament: Tournament;
  export let friend_codes: FriendCode[];
  export let selected_fc_id: number | null = null;
  export let mii_name: string | null = null;
  export let can_host = false;

  $: console.log(tournament);
</script>

{#if tournament.require_single_fc}
  <div class="item">
    <span class="item-label">
      <label for="selected_fc_id">Select FC</label>
    </span>
    
    <select name="selected_fc_id" value={selected_fc_id} required>
      {#each friend_codes as fc}
        <option value={fc.id}>{fc.fc}</option>
      {/each}
    </select>
  </div>
{/if}
{#if tournament.mii_name_required}
  <div class="item">
    <span class="item-label">
      <label for="mii_name">In-game/Mii Name</label>
    </span>
    <input name="mii_name" maxlength={tournament.game === 'mkt' ? 12 : 10} value={mii_name} required />
  </div>
{/if}
{#if tournament.host_status_required}
  <div class="item">
    <span class="item-label">
      <label for="can_host">Can host?</label>
    </span>
    
    <select name="can_host" value={Boolean(can_host)} required>
      <option value={false}>No</option>
      <option value={true}>Yes</option>
    </select>
  </div>
{/if}

<style>
  .item-label {
    display: inline-block;
    width: 150px;
    font-weight: 525;
  }
  .item {
    margin: 10px 0;
  }
</style>
