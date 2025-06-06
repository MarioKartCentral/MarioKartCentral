<script lang="ts">
    import type { TeamTransfer, TransferList } from "$lib/types/team-transfer";
    import Dialog from "$lib/components/common/Dialog.svelte";
    import { onMount } from "svelte";
    import { locale } from "$i18n/i18n-svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import { page } from "$app/stores";
    import TagBadge from "$lib/components/badges/TagBadge.svelte";
    import ArrowRight from "$lib/components/common/ArrowRight.svelte";
    import ConfirmButton from "$lib/components/common/buttons/ConfirmButton.svelte"
    import CancelButton from "$lib/components/common/buttons/CancelButton.svelte"
    import Button from "$lib/components/common/buttons/Button.svelte"
    import GameBadge from "$lib/components/badges/GameBadge.svelte";
    import ModeBadge from "$lib/components/badges/ModeBadge.svelte";
    import PageNavigation from "$lib/components/common/PageNavigation.svelte";
    import GameModeSelect from "$lib/components/common/GameModeSelect.svelte";
    import BaggerBadge from "$lib/components/badges/BaggerBadge.svelte";
    import LL from "$i18n/i18n-svelte";

    export let approval_status: "approved" | "pending" | "denied";
    export let team_id: number | null = null;
    export let roster_id: number | null = null;

    let transfers: TeamTransfer[] = [];
    let deny_dialog: Dialog;
    let curr_transfer: TeamTransfer;
    let send_back = false;

    let page_number = 1;
    let total_pages = 0;

    let game: string | null = null;
    let mode: string | null = null;
    let from: string | null = null;
    let to: string | null = null;

    $: {
        if(roster_id) {
            game = null;
            mode = null;
        }
    }
    
    async function fetchData() {
        let url = `/api/registry/teams/transfers/${approval_status}?page=${page_number}`;
        if(game !== null) {
            url += `&game=${game}`;
        }
        if(mode !== null) {
            url += `&mode=${mode}`;
        }
        if(team_id !== null) {
            url += `&team_id=${team_id}`;
        }
        if(roster_id !== null) {
            url += `&roster_id=${roster_id}`;
        }
        if(from) {
            url += `&from_date=${new Date(from).getTime()/1000}`;
        }
        if(to) {
            url += `&to_date=${new Date(to).getTime()/1000}`;
        }
        const res = await fetch(url);
        if (res.status !== 200) {
            return;
        }
        const body: TransferList = await res.json();
        transfers = body.transfers;
        total_pages = body.page_count;
    }

    async function search() {
        page_number = 1;
        fetchData();
    }

    onMount(fetchData);

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'medium',
        timeStyle: 'short'
    };

    async function approveTransfer(transfer: TeamTransfer) {
        let conf = window.confirm($LL.MODERATOR.APPROVE_TRANSFER_CONFIRM());
        if(!conf) return;
        const payload = {
            invite_id: transfer.invite_id,
        };
        const endpoint = '/api/registry/teams/approveTransfer';
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (res.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.MODERATOR.APPROVE_TRANSFER_FAILED()}: ${result['title']}`);
        }
    }
    
  async function denyTransfer(transfer: TeamTransfer) {
    deny_dialog.close();
    const payload = {
      invite_id: transfer.invite_id,
      send_back: Boolean(send_back),
    };
    console.log(payload);
    const endpoint = '/api/registry/teams/denyTransfer';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.DENY_TRANSFER_FAILED()}: ${result['title']}`);
    }
  }

  function denyDialog(invite: TeamTransfer) {
    curr_transfer = invite;
    deny_dialog.open();
  }
</script>


<form on:submit|preventDefault={search}>
    <div class="top">
        {#if !team_id}
            <GameModeSelect bind:game={game} bind:mode={mode} flex all_option hide_labels inline is_team/>
        {/if}
        <div class="option">
            <label for="from">{$LL.COMMON.FROM()}</label>
            <input name="from" type="datetime-local" bind:value={from}/>
        </div>
        <div class="option">
            <label for="to">{$LL.COMMON.TO()}</label>
            <input name="to" type="datetime-local" bind:value={to}/>
        </div>
        <div class="option">
            <Button type="submit">{$LL.COMMON.FILTER()}</Button>
        </div>
    </div>
</form>

{#if transfers.length}
    <PageNavigation bind:currentPage={page_number} totalPages={total_pages} refresh_function={fetchData}/>
    <div class="transfers">
        {#each transfers as transfer}
            <div class="row">
                <div class="date field">
                    {new Date(transfer.date * 1000).toLocaleString($locale, options)}
                </div>
                <div class="left field">
                    <div class="flag">
                        <Flag country_code={transfer.player_country_code}/>
                    </div>
                    <a href="/{$page.params.lang}/registry/players/profile?id={transfer.player_id}">
                        {transfer.player_name}
                        {#if transfer.is_bagger_clause}
                            <BaggerBadge/>
                        {/if}
                    </a>
                </div>
                <div class="badges field">
                    <GameBadge game={transfer.game}/>
                    <ModeBadge mode={transfer.mode}/>
                </div>
                <div class="right field">
                    {#if transfer.roster_leave}
                        <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_leave.team_id}">
                            <TagBadge tag={transfer.roster_leave.roster_tag} color={transfer.roster_leave.team_color}/>
                        </a>
                    {:else}
                        {$LL.TEAMS.TRANSFERS.NO_TEAM()}
                    {/if}
                    <ArrowRight/>
                    {#if transfer.roster_join}
                        <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_join.team_id}">
                            <TagBadge tag={transfer.roster_join.roster_tag} color={transfer.roster_join.team_color}/>
                        </a>
                    {:else}
                        {$LL.TEAMS.TRANSFERS.NO_TEAM()}
                    {/if}
                </div>
                {#if approval_status === "pending"}
                    <div class="approve field">
                        <ConfirmButton on:click={() => approveTransfer(transfer)}/>
                        <CancelButton on:click={() => denyDialog(transfer)}/>
                    </div>
                {/if}
            </div>
        {/each}
    </div>
    <PageNavigation bind:currentPage={page_number} totalPages={total_pages} refresh_function={fetchData}/>
{:else}
    {$LL.TEAMS.TRANSFERS.NO_TRANSFERS()}
{/if}

<Dialog bind:this={deny_dialog} header={$LL.MODERATOR.DENY_TRANSFER()}>
    <div>
        {$LL.MODERATOR.SEND_TRANSFER_BACK()}
    </div>
    <input type="checkbox" bind:value={send_back} />
    <br /><br />
    <div>
        <Button on:click={() => denyTransfer(curr_transfer)}>{$LL.MODERATOR.DENY()}</Button>
        <Button on:click={deny_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
    </div>
</Dialog>

<style>
    .transfers {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .top {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 10px;
    }
    .row {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        align-items: center;
        font-size: 0.9rem;
        background-color: rgba(255, 255, 255, 0.15);
        padding: 12px;
        min-height: 75px;
    }
    .row:nth-child(odd) {
        background-color: rgba(210, 210, 210, 0.15);
    }
    .flag {
        zoom: 85%;
    }
    .date {
        min-width: 200px;
    }
    .field {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 5px;
    }
    .left {
        min-width: 200px;
    }
    .right {
        min-width: 300px;
    }
    .badges {
        min-width: 200px;
    }
    .approve {
        min-width: 100px;
    }
  </style>