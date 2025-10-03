<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import DOMPurify from 'dompurify';
  import type { BanInfoBasic } from '$lib/types/ban-info';
  import { page } from '$app/stores';

  export let ban_info: BanInfoBasic;

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
    timeStyle: 'short',
  };
  const unbanText = getUnbanText();

  function getUnbanText() {
    if (ban_info.is_indefinite) {
      return $LL.PLAYER_BAN.INDEFINITE();
    }
    if (ban_info.unban_date) {
      return new Date(ban_info.unban_date * 1000).toLocaleString($page.params.lang, options);
    }
    return '';
  }
</script>

<div class="container">
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html DOMPurify.sanitize($LL.PLAYER_BAN.THIS_PLAYER_IS_BANNED(), { ALLOWED_TAGS: ['strong'] })} <br />
  <strong>{$LL.PLAYER_BAN.REASON()}</strong>{`: ${ban_info.reason}`} <br />
  {#if unbanText}
    <strong>{$LL.PLAYER_BAN.UNBAN_DATE()}</strong>{`: ${unbanText}`}
  {/if}
</div>

<style>
  div.container {
    width: 50%;
    margin: 20px auto;
    background-color: darkred;
    color: #de858f;
    padding: 5px;
  }
</style>
