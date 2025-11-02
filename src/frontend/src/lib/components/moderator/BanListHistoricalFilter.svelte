<script lang="ts">
  import type { BanHistoricalFilter } from '$lib/types/ban-filter';
  import LL from '$i18n/i18n-svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';

  export let filter: BanHistoricalFilter;
  export let handleSubmit: () => void;

  function getDate(value: string, isBefore: boolean) {
    if (!value) return null;

    const date = new Date(`${value} ${isBefore ? '23:59:59' : ''}`);
    return Math.ceil(date.getTime() / 1000); // divide by 1000 since Python uses seconds instead of ms
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <div>
    <label for="player">{$LL.PLAYER_BAN.PLAYER(1)}</label> <br />
    <input name="player" type="text" bind:value={filter.name} placeholder={$LL.PLAYER_BAN.SEARCH_BY_NAME()} />
  </div>
  <div>
    <label for="bannedBy">{$LL.PLAYER_BAN.BANNED_BY()}</label> <br />
    <input name="bannedBy" type="text" bind:value={filter.banned_by} placeholder={$LL.PLAYER_BAN.SEARCH_BY_NAME()} />
  </div>
  <div>
    <label for="unbannedBy">{$LL.PLAYER_BAN.UNBANNED_BY()}</label> <br />
    <input
      name="unbannedBy"
      type="text"
      bind:value={filter.unbanned_by}
      placeholder={$LL.PLAYER_BAN.SEARCH_BY_NAME()}
    />
  </div>
  <div>
    <label for="isIndefinite">{$LL.PLAYER_BAN.IS_INDEFINITE()}</label> <br />
    <select name="isIndefinite" bind:value={filter.is_indefinite}>
      <option value={null}></option>
      <option value={true}>{$LL.PLAYER_BAN.YES()}</option>
      <option value={false}>{$LL.PLAYER_BAN.NO()}</option>
    </select>
  </div>
  <div>
    <label for="bannedAfter">{$LL.PLAYER_BAN.BANNED_FROM()}</label> <br />
    <input
      name="bannedAfter"
      type="date"
      on:change={(event) => {
        filter.banned_after = getDate(event.currentTarget.value, false);
      }}
    />
  </div>
  <div>
    <label for="bannedBefore">{$LL.PLAYER_BAN.BANNED_TO()}</label> <br />
    <input
      name="bannedBefore"
      type="date"
      on:change={(event) => {
        filter.banned_before = getDate(event.currentTarget.value, true);
      }}
    />
  </div>
  <div>
    <label for="unbannedAfter">{$LL.PLAYER_BAN.UNBANNED_FROM()}</label> <br />
    <input
      name="unbannedAfter"
      type="date"
      on:change={(event) => {
        filter.unbanned_after = getDate(event.currentTarget.value, false);
      }}
    />
  </div>
  <div>
    <label for="unbannedBefore">{$LL.PLAYER_BAN.UNBANNED_TO()}</label> <br />
    <input
      name="unbannedBefore"
      type="date"
      on:change={(event) => {
        filter.unbanned_before = getDate(event.currentTarget.value, true);
      }}
    />
  </div>
  <div>
    <label for="reason">{$LL.PLAYER_BAN.REASON()}</label> <br />
    <input name="reason" type="text" bind:value={filter.reason} placeholder={$LL.PLAYER_BAN.REASON()} />
  </div>
  <div>
    <label for="comment">{$LL.PLAYER_BAN.COMMENT()}</label> <br />
    <input name="comment" type="text" bind:value={filter.comment} placeholder={$LL.PLAYER_BAN.COMMENT_INCLUDES()} />
  </div>
  <div>
    <Button type="submit">{$LL.COMMON.SEARCH()}</Button>
  </div>
</form>

<style>
  form {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 10px;
  }
</style>
