<script lang="ts">
  import type { FriendCode } from '$lib/types/friend-code';
  import type { Tournament } from '$lib/types/tournament';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import LL from '$i18n/i18n-svelte';
  import Input from '$lib/components/common/Input.svelte';

  export let tournament: Tournament;
  export let friend_codes: FriendCode[];
  export let selected_fc_id: number | null = null;
  export let mii_name: string | null = null;
  export let can_host = false;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
</script>

{#if tournament.require_single_fc}
  <div class="item">
    <span class="item-label">
      <label for="selected_fc_id">{$LL.TOURNAMENTS.REGISTRATIONS.SELECT_FC()}</label>
    </span>
    
    <select name="selected_fc_id" value={selected_fc_id} required>
      <option value={null} selected disabled>{$LL.TOURNAMENTS.REGISTRATIONS.SELECT_A_FRIEND_CODE()}</option>
      {#each friend_codes.filter((f) => f.is_active) as fc}
        <option value={fc.id}>{fc.fc}</option>
      {/each}
    </select>
  </div>
{/if}
{#if tournament.mii_name_required}
  <div class="item">
    <span class="item-label">
      <label for="mii_name">{$LL.TOURNAMENTS.REGISTRATIONS.IN_GAME_MII_NAME()}</label>
    </span>
    <Input name="mii_name" maxlength={tournament.game === 'mkt' ? 12 : 10} value={mii_name} required no_white_space/>
  </div>
{/if}
{#if tournament.host_status_required}
  <div class="item">
    <span class="item-label">
      <label for="can_host">{$LL.TOURNAMENTS.REGISTRATIONS.CAN_HOST()}</label>
    </span>
    
    <select name="can_host" value={Boolean(can_host)} required>
      <option value={false}>{$LL.COMMON.NO()}</option>
      <option value={true} disabled={!check_tournament_permission(user_info, tournament_permissions.register_host, tournament.id, 
      tournament.series_id, true)}>{$LL.COMMON.YES()}</option>
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
