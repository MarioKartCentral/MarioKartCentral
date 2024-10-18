<script lang="ts">
    import LL from '$i18n/i18n-svelte';
    import type { BanInfoDetailed } from '$lib/types/ban-info';
    import Table from '$lib/components/common/Table.svelte';
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { page } from '$app/stores';
    import Flag from '$lib/components/common/Flag.svelte';
    import Dialog from '$lib/components/common/Dialog.svelte';
    import ViewEditBan from '$lib/components/moderator/ViewEditBan.svelte';
    import BanDetails from '$lib/components/moderator/BanDetails.svelte';

    export let banInfoDetailedArray: BanInfoDetailed[];
    export let isHistorical: boolean = false;
    
    let dialog: Dialog;
    let selectedBanInfo: BanInfoDetailed | null;

    function datetimeToString(datetime: number | null) {
      if (datetime === null)
        return '';
      const date = new Date(datetime * 1000);
      return date.toLocaleString().split(",")[0];
    };

    function handleClick(banInfo: BanInfoDetailed) {
      selectedBanInfo = banInfo;
      dialog.open();
    };
  </script>
  
  <Table>
    <col class="w5"/> <!-- flag -->
    <col class="w20"/> <!-- name -->
    <col class="w10 mobile-hide"/> <!-- ban date -->
    <col class="w10 mobile-hide"/> <!-- expiration date / unban date -->
    <col class="w15"/> <!-- reason -->
    <col class="w10 mobile-hide"/> <!-- banned by -->
    <col class="w10 mobile-hide"/> <!-- unbanned by -->
    <col class="w15"/> <!-- view details button -->
    <thead>
      <tr>
        <th></th>
        <th>{$LL.PLAYER_BAN.NAME()}</th>
        <th class="mobile-hide">{$LL.PLAYER_BAN.BANNED()}</th>
        <th class="mobile-hide">{#if isHistorical} {$LL.PLAYER_BAN.UNBANNED()} {:else} {$LL.PLAYER_BAN.EXPIRES()} {/if}</th>
        <th>{$LL.PLAYER_BAN.REASON()}</th>
        <th class="mobile-hide">{$LL.PLAYER_BAN.BANNED_BY()}</th>
        <th class="mobile-hide">{isHistorical ? $LL.PLAYER_BAN.UNBANNED_BY() : ""}</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each banInfoDetailedArray as bid, i}
        <tr class="row-{i % 2}">
          <td><Flag country_code={bid.player_country_code} /></td>
          <td><a href="/{$page.params.lang}/registry/players/profile?id={bid.player_id}">{bid.player_name}</a></td>
          <td class="mobile-hide">{datetimeToString(bid.ban_date)}</td>
          {#if isHistorical}
            <td class="mobile-hide">{datetimeToString(bid.unban_date)}</td>
          {:else}
            <td class="mobile-hide">{bid.is_indefinite ? $LL.PLAYER_BAN.INDEFINITE() : datetimeToString(bid.expiration_date)}</td>
          {/if}
          <td>{bid.reason}</td>
          {#if bid.banned_by_pid}
            <td class="mobile-hide"><a href="/{$page.params.lang}/registry/players/profile?id={bid.banned_by_pid}">{bid.banned_by_name}</a></td>
          {:else}
            <td class="mobile-hide">User {bid.banned_by_uid}</td>
          {/if}
          {#if isHistorical}
            {#if bid.unbanned_by_pid !== null}
              <td class="mobile-hide"><a href="/{$page.params.lang}/registry/players/profile?id={bid.unbanned_by_pid}">{bid.unbanned_by_name}</a></td>
            {:else if bid.unbanned_by_uid !== null}
              <td class="mobile-hide">User {bid.unbanned_by_uid}</td>
            {:else}
              <td class="mobile-hide">SYSTEM</td>
            {/if}
            <td><Button on:click={() => handleClick(bid)}>{$LL.PLAYER_BAN.BAN_DETAILS()}</Button></td>
          {:else}
            <td class="mobile-hide"></td>
            <td><Button on:click={() => handleClick(bid)}>{$LL.PLAYER_BAN.VIEW_EDIT_BAN()}</Button></td>
          {/if}
        </tr>
      {/each}
    </tbody>
  </Table>

  <Dialog bind:this={dialog} header={$LL.PLAYER_BAN.BAN_PLAYER()}>
    {#if selectedBanInfo}
      {#if isHistorical}
        <BanDetails banInfo={selectedBanInfo} />
      {:else}
        <ViewEditBan banInfo={selectedBanInfo} />
      {/if}
    {/if}
  </Dialog>
  
  <style>
    .w20 {
        width: 20%;
    }
    .w15 {
        width: 15%;
    }
    .w10 {
        width: 10%;
    }
    .w5 {
        width: 5%;
    }
  </style>
  