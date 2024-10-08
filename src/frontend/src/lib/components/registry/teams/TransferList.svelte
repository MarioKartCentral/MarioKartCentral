<script lang="ts">
    import type { TeamTransfer } from "$lib/types/team-transfer";
    import Dialog from "$lib/components/common/Dialog.svelte";
    import Table from "$lib/components/common/Table.svelte";
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

    export let approval_status: "approved" | "pending" | "denied";

    let transfers: TeamTransfer[] = [];
    let deny_dialog: Dialog;
    let curr_transfer: TeamTransfer;
    let send_back = false;

    let page_number = 1;
    let total_pages = 0;

    type TransferList = {
        transfers: TeamTransfer[];
        transfer_count: number;
        page_count: number;
    }
    let game: string | null = null;
    let mode: string | null = null;
    
    async function fetchData() {
        let url = `/api/registry/teams/transfers/${approval_status}?page=${page_number}`;
        if(game !== null) {
            url += `&game=${game}`;
        }
        if(mode !== null) {
            url += `&mode=${mode}`;
        }
        const res = await fetch(url);
        if (res.status !== 200) {
            return;
        }
        const body: TransferList = await res.json();
        transfers = body.transfers;
        total_pages = body.page_count;
    }

    onMount(fetchData);

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'medium',
        timeStyle: 'short'
    };

    async function approveTransfer(transfer: TeamTransfer) {
        let conf = window.confirm("Are you sure you want to approve this transfer?");
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
            alert(`Approving transfer failed: ${result['title']}`);
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
      alert(`Approving transfer failed: ${result['title']}`);
    }
  }

  function denyDialog(invite: TeamTransfer) {
    curr_transfer = invite;
    deny_dialog.open();
  }
</script>

<form on:submit|preventDefault={fetchData}>
    <div class="flex">
        <GameModeSelect bind:game={game} bind:mode={mode} flex all_option hide_labels inline/>
        <Button type="submit">Filter</Button>
    </div>
</form>
{#if transfers.length}
    <PageNavigation bind:currentPage={page_number} totalPages={total_pages} refresh_function={fetchData}/>
    <Table>
        <col class="country"/>
        <col class="name" />
        <col class="gamemode mobile-hide"/>
        <col class="between" />
        <col class="date mobile-hide" />
        {#if approval_status === "pending"}
            <col class="approve" />
        {/if}
        <thead>
        <tr>
            <th></th>
            <th>Player</th>
            <th class="mobile-hide">Game/Mode</th>
            <th></th>
            <th class="mobile-hide">Date</th>
            {#if approval_status === "pending"}
                <th>Approve?</th>
            {/if}
        </tr>
        </thead>
        <tbody>
        {#each transfers as transfer, i}
            <tr class="row-{i % 2}">
            <td>
                <Flag country_code={transfer.player_country_code}/>
            </td>
            <td>
                <a href="/{$page.params.lang}/registry/players/profile?id={transfer.player_id}">
                    {transfer.player_name}
                </a>
            </td>
            <td class="mobile-hide">
                <GameBadge game={transfer.game}/>
                <ModeBadge mode={transfer.mode}/>
            </td>
            <td>
                <div class="flex">
                    {#if transfer.roster_leave}
                        <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_leave.team_id}">
                            <TagBadge tag={transfer.roster_leave.roster_tag} color={transfer.roster_leave.team_color}/>
                        </a>
                        
                    {:else}
                        No team
                    {/if}
                    <ArrowRight/>
                    {#if transfer.roster_join}
                        <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_join.team_id}">
                            <TagBadge tag={transfer.roster_join.roster_tag} color={transfer.roster_join.team_color}/>
                        </a>
                    {:else}
                        No team
                    {/if}
                </div>
                
            </td>
            <td class="mobile-hide">{new Date(transfer.date * 1000).toLocaleString($locale, options)}</td>
            {#if approval_status === "pending"}
                <td>
                    <ConfirmButton on:click={() => approveTransfer(transfer)}/>
                    <CancelButton on:click={() => denyDialog(transfer)}/>
                </td>
            {/if}
            </tr>
        {/each}
        </tbody>
    </Table>
{:else}
    No transfers.
{/if}

<Dialog bind:this={deny_dialog} header="Deny Transfer">
<div>
    Send transfer back to the player?
</div>
<input type="checkbox" bind:value={send_back} />
<br /><br />
<div>
    <Button on:click={() => denyTransfer(curr_transfer)}>Deny</Button>
    <Button on:click={deny_dialog.close}>Cancel</Button>
</div>
</Dialog>

<style>
    div.flex {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
    }
    col.country {
        width: 15%;
    }
    col.name {
        width: 20%;
    }
    col.gamemode {
        width: 15%;
    }
    col.between {
        width: 20%;
    }
    col.date {
        width: 15%;
    }
    col.approve {
        width: 15%;
    }
  </style>