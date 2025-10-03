<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import type { BanInfoDetailed } from '$lib/types/ban-info';
  import { findNumberOfDaysBetweenDates } from '$lib/util/util';

  export let banInfo: BanInfoDetailed;

  $: daysRemaining = getDaysRemaining(banInfo);
  $: duration = findNumberOfDaysBetweenDates(banInfo.ban_date, banInfo.expiration_date);

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };

  function getDaysRemaining(banInfo: BanInfoDetailed) {
    const nowSeconds = Math.floor(Date.now() / 1000);
    const days = Math.max(-1, findNumberOfDaysBetweenDates(nowSeconds, banInfo.expiration_date));
    return days >= 0 ? $LL.PLAYER_BAN.IN_COUNT_DAYS({ count: days }) : '';
  }

  function unixTimestampToString(timestamp: number) {
    let date = new Date(timestamp * 1000);
    return date.toLocaleString($page.params.lang, options);
  }
</script>

<div>
  <h2>{$LL.PLAYER_BAN.BAN_DETAILS()}</h2>
  <strong>{$LL.PLAYER_BAN.PLAYER(1)}</strong>:
  <a href={`/${$page.params.lang}/registry/players/profile?id=${banInfo.player_id}`}><u>{banInfo.player_name}</u></a>
  <br />
  <strong>{$LL.PLAYER_BAN.BANNED_BY()}</strong>: {#if banInfo.banned_by_pid}
    <a href={`/${$page.params.lang}/registry/players/profile?id=${banInfo.banned_by_pid}`}
      ><u>{banInfo.banned_by_name}</u></a
    >
  {:else}
    {$LL.PLAYER_BAN.USER({ userId: banInfo.banned_by_uid })}
  {/if} <br />
  <strong>{$LL.PLAYER_BAN.IS_INDEFINITE()}</strong>: {banInfo.is_indefinite
    ? $LL.PLAYER_BAN.YES()
    : $LL.PLAYER_BAN.NO()} <br />
  <strong>{$LL.PLAYER_BAN.BANNED()}</strong>: {unixTimestampToString(banInfo.ban_date)} <br />
  {#if !banInfo.is_indefinite}
    <strong>{$LL.PLAYER_BAN.EXPIRES()}</strong>: {unixTimestampToString(banInfo.expiration_date)} {daysRemaining}<br />
  {/if}
  {#if banInfo.unban_date}
    <strong>{$LL.PLAYER_BAN.UNBANNED()}</strong>: {unixTimestampToString(banInfo.unban_date)}<br />
    <strong>{$LL.PLAYER_BAN.UNBANNED_BY()}</strong>: {#if banInfo.unbanned_by_pid}
      <a href={`/${$page.params.lang}/registry/players/profile?id=${banInfo.unbanned_by_pid}`}
        ><u>{banInfo.unbanned_by_name}</u></a
      >
    {:else if banInfo.unbanned_by_uid !== null}
      {$LL.PLAYER_BAN.USER({ userId: banInfo.unbanned_by_uid })}
    {:else}
      SYSTEM
    {/if} <br />
  {/if}
  {#if !banInfo.is_indefinite}
    <strong>{$LL.PLAYER_BAN.DURATION()}</strong>: {$LL.PLAYER_BAN.COUNT_DAYS({ count: duration })} <br />
  {/if}
  <strong>{$LL.PLAYER_BAN.REASON()}</strong>: {banInfo.reason} <br />
  <div class="comment">
    <strong>{$LL.PLAYER_BAN.COMMENT()}</strong>:
    <span>{banInfo.comment}</span>
  </div>
</div>

<style>
  h2 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 5px;
  }
  .comment {
    display: flex;
  }
  .comment > span {
    white-space: pre-line;
    margin-left: 3px;
  }
</style>
