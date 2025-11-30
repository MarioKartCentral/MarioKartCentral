<script lang="ts">
  import { onMount } from 'svelte';
  import type { TeamEditRequest, TeamEditList } from '$lib/types/team-edit-request';
  import Table from '../common/table/Table.svelte';
  import LL from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import TagBadge from '../badges/TagBadge.svelte';
  import ArrowRight from '../common/ArrowRight.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import ConfirmButton from '../common/buttons/ConfirmButton.svelte';
  import CancelButton from '../common/buttons/CancelButton.svelte';
  import PageNavigation from '../common/PageNavigation.svelte';
  import Flag from '../common/Flag.svelte';
  import Button from '../common/buttons/Button.svelte';

  export let approval_status: string;

  let currentPage = 1;
  let totalChanges = 0;
  let totalPages = 0;
  let team_requests: TeamEditRequest[] = [];

  async function fetchData() {
    const team_res = await fetch(
      `/api/registry/teams/changeRequests?approval_status=${approval_status}&page=${currentPage}`,
    );
    if (team_res.status === 200) {
      const body: TeamEditList = await team_res.json();
      team_requests = body.change_list;
      totalChanges = body.count;
      totalPages = body.page_count;
    }
  }

  onMount(fetchData);

  async function approveTeamRequest(request: TeamEditRequest) {
    let conf = window.confirm($LL.MODERATOR.APPROVE_TEAM_EDIT_CONFIRM());
    if (!conf) return;
    const payload = {
      request_id: request.id,
    };
    const res = await fetch(`/api/registry/teams/approveChange`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.APPROVE_TEAM_EDIT_FAILED()}: ${result['title']}`);
    }
  }

  async function denyTeamRequest(request: TeamEditRequest) {
    let conf = window.confirm($LL.MODERATOR.DENY_TEAM_EDIT_CONFIRM());
    if (!conf) return;
    const payload = {
      request_id: request.id,
    };
    const res = await fetch(`/api/registry/teams/denyChange`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.DENY_TEAM_EDIT_FAILED()}: ${result['title']}`);
    }
  }

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };
</script>

{#if team_requests.length}
  {$LL.MODERATOR.TEAM_EDIT_COUNT({ count: totalChanges })}
  <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
  <Table data={team_requests} let:item={request}>
    <colgroup slot="colgroup">
      <col class="tag" />
      <col class="name" />
      <col class="date mobile-hide" />
      {#if approval_status === 'pending'}
        <col class="approve" />
      {/if}
      {#if approval_status !== 'pending'}
        <col class="handled-by mobile-hide" />
      {/if}
      {#if approval_status === 'approved'}
        <col class="delete" />
      {/if}
    </colgroup>
    <tr slot="header">
      <th>
        {$LL.COMMON.TAG()}
      </th>
      <th>
        {$LL.COMMON.NAME()}
      </th>
      <th class="mobile-hide">
        {$LL.COMMON.DATE()}
      </th>
      {#if approval_status === 'pending'}
        <th>{$LL.MODERATOR.APPROVE()}</th>
      {/if}
      {#if approval_status !== 'pending'}
        <th class="mobile-hide">{$LL.MODERATOR.HANDLED_BY()}</th>
      {/if}
      {#if approval_status === 'approved'}
        <th>{$LL.COMMON.DELETE()}</th>
      {/if}
    </tr>

    <tr class="row">
      <td>
        <a href="/{$page.params.lang}/registry/teams/profile?id={request.team_id}">
          <div class="flex">
            <TagBadge tag={request.old_tag} color={request.color} />
            {#if request.old_tag !== request.new_tag}
              <ArrowRight />
              <TagBadge tag={request.new_tag} color={request.color} />
            {/if}
          </div>
        </a>
      </td>
      <td>
        <a href="/{$page.params.lang}/registry/teams/profile?id={request.team_id}">
          <div class="flex">
            {request.old_name}
            {#if request.old_name !== request.new_name}
              <ArrowRight />
              {request.new_name}
            {/if}
          </div>
        </a>
      </td>
      <td class="mobile-hide">{new Date(request.date * 1000).toLocaleString($locale, options)}</td>
      {#if approval_status === 'pending'}
        <td>
          <ConfirmButton on:click={() => approveTeamRequest(request)} />
          <CancelButton on:click={() => denyTeamRequest(request)} />
        </td>
      {/if}
      {#if approval_status !== 'pending'}
        <td class="mobile-hide">
          {#if request.handled_by}
            <a href="/{$page.params.lang}/registry/players/profile?id={request.handled_by.id}">
              <div class="flex handled-by">
                <Flag country_code={request.handled_by.country_code} />
                <div>
                  {request.handled_by.name}
                </div>
              </div>
            </a>
          {/if}
        </td>
      {/if}
      {#if approval_status === 'approved'}
        <td>
          <Button on:click={() => denyTeamRequest(request)}>{$LL.COMMON.DELETE()}</Button>
        </td>
      {/if}
    </tr>
  </Table>
  <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
{:else}
  {$LL.MODERATOR.NO_TEAM_EDIT_REQUESTS()}
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
