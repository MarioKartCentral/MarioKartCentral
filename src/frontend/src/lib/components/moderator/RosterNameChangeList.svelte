<script lang="ts">
    import type { RosterEditRequest, RosterEditList } from "$lib/types/roster-edit-request";
    import Table from "../common/Table.svelte";
    import LL from "$i18n/i18n-svelte";
    import { page } from "$app/stores";
    import TagBadge from "../badges/TagBadge.svelte";
    import ArrowRight from "../common/ArrowRight.svelte";
    import { locale } from "$i18n/i18n-svelte";
    import ConfirmButton from "../common/buttons/ConfirmButton.svelte";
    import CancelButton from "../common/buttons/CancelButton.svelte";
    import { onMount } from "svelte";
    import PageNavigation from "../common/PageNavigation.svelte";
    import Flag from "../common/Flag.svelte";
    import Button from "../common/buttons/Button.svelte";

    export let approval_status: string;

    let currentPage = 1;
    let totalChanges = 0;
    let totalPages = 0;
    let roster_requests: RosterEditRequest[] = [];

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };

    async function fetchData() {
        const roster_res = await fetch(`/api/registry/teams/rosterChangeRequests?approval_status=${approval_status}&page=${currentPage}`);
        if (roster_res.status === 200) {
            const body: RosterEditList = await roster_res.json();
            roster_requests = body.change_list;
            totalChanges = body.count;
            totalPages = body.page_count;
        }
    }

    onMount(fetchData);

    async function approveRosterRequest(request: RosterEditRequest) {
        let conf = window.confirm($LL.MODERATOR.APPROVE_ROSTER_EDIT_CONFIRM());
        if(!conf) return;
            const payload = {
            request_id: request.id,
        };
        const res = await fetch(`/api/registry/teams/approveRosterChange`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (res.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.MODERATOR.APPROVE_ROSTER_EDIT_FAILED()}: ${result['title']}`);
        }
    }

  async function denyRosterRequest(request: RosterEditRequest) {
    let conf = window.confirm($LL.MODERATOR.DENY_ROSTER_EDIT_CONFIRM());
    if(!conf) return;
    const payload = {
      request_id: request.id,
    };
    const res = await fetch(`/api/registry/teams/denyRosterChange`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.DENY_ROSTER_EDIT_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if roster_requests.length}
    {$LL.MODERATOR.ROSTER_EDIT_COUNT({count: totalChanges})}
    <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
    <Table>
      <col class="tag"/>
      <col class="name"/>
      <col class="date mobile-hide"/>
        {#if approval_status === "pending"}
            <col class="approve">
        {/if}
        {#if approval_status !== "pending"}
            <col class="handled-by mobile-hide">
        {/if}
        {#if approval_status === "approved"}
            <col class="delete">
        {/if}
        <thead>
            <tr>
            <th>{$LL.COMMON.TAG()}</th>
            <th>{$LL.COMMON.NAME()}</th>
            <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
            {#if approval_status === "pending"}
                <th>{$LL.MODERATOR.APPROVE()}</th>
            {/if}
            {#if approval_status !== "pending"}
                <th class="mobile-hide">{$LL.MODERATOR.HANDLED_BY()}</th>
            {/if}
            {#if approval_status === "approved"}
                <th>{$LL.COMMON.DELETE()}</th>
            {/if}
            </tr>
        </thead>
        <tbody>
            {#each roster_requests as r, i}
            <tr class="row-{i % 2}">
                <td>
                <a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">
                    <div class="flex">
                    <TagBadge tag={r.old_tag} color={r.color}/>
                    {#if r.old_tag !== r.new_tag}
                    <ArrowRight/>
                    <TagBadge tag={r.new_tag} color={r.color}/>
                    {/if}
                    </div>
                </a>
                </td>
                <td>
                <a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">
                    <div class="flex">
                    {r.old_name}
                    {#if r.old_name !== r.new_name}
                    <ArrowRight/>
                    {r.new_name}
                    {/if}
                    </div>
                </a>
                </td>
                <td class="mobile-hide">{new Date(r.date * 1000).toLocaleString($locale, options)}</td>
                {#if approval_status === "pending"}
                <td>
                <ConfirmButton on:click={() => approveRosterRequest(r)}/>
                <CancelButton on:click={() => denyRosterRequest(r)}/>
                </td>
            {/if}
            {#if approval_status !== "pending"}
                <td class="mobile-hide">
                    {#if r.handled_by}
                        <a href="/{$page.params.lang}/registry/players/profile?id={r.handled_by.id}">
                            <div class="flex handled-by">      
                                <Flag country_code={r.handled_by.country_code}/>
                                <div>
                                    {r.handled_by.name}
                                </div>
                            </div>
                        </a>
                    {/if}
                </td>
            {/if}
            {#if approval_status === "approved"}
                <td>
                    <Button on:click={() => denyRosterRequest(r)}>{$LL.COMMON.DELETE()}</Button>
                </td>
            {/if}
            </tr>
            {/each}
        </tbody>
    </Table>
    <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
{:else}
    {$LL.MODERATOR.NO_ROSTER_EDIT_REQUESTS()}
{/if}

<style>
  .flex {
      display: flex;
      flex-direction: row;
      align-items: center;
  }
  div.handled-by {
      gap: 10px;
  }
  col.tag {
      width: 20%;
  }
  col.name {
      width: 25%;
  }
  col.date {
      width: 20%;
  }
  col.approve {
      width: 20%;
  }
  col.handled-by {
      width: 15%;
  }
  col.delete {
      width: 25%;
  }
</style>