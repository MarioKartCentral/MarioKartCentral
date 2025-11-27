<script lang="ts">
  import type { PlayerNameChangeRequestList, PlayerNameChangeRequest } from '$lib/types/player-name-change-request';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import Table from '../common/table/Table.svelte';
  import Flag from '../common/Flag.svelte';
  import { page } from '$app/stores';
  import ArrowRight from '../common/ArrowRight.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import ConfirmButton from '$lib/components/common/buttons/ConfirmButton.svelte';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import PageNavigation from '../common/PageNavigation.svelte';
  import Button from '../common/buttons/Button.svelte';

  export let approval_status: string;

  let currentPage = 1;
  let totalChanges = 0;
  let totalPages = 0;
  let name_requests: PlayerNameChangeRequest[] = [];

  async function fetchData() {
    const res = await fetch(`/api/registry/players/nameChanges?approval_status=${approval_status}&page=${currentPage}`);
    if (res.status === 200) {
      const body: PlayerNameChangeRequestList = await res.json();
      name_requests = body.change_list;
      totalPages = body.page_count;
      totalChanges = body.count;
    }
  }

  onMount(fetchData);

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };

  async function approveNameRequest(request: PlayerNameChangeRequest) {
    let conf = window.confirm($LL.MODERATOR.APPROVE_NAME_REQUEST_CONFIRM());
    if (!conf) return;
    const payload = {
      request_id: request.id,
    };
    const res = await fetch(`/api/registry/players/approveNameChange`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.APPROVE_NAME_REQUEST_FAILED()}: ${result['title']}`);
    }
  }

  async function denyNameRequest(request: PlayerNameChangeRequest) {
    let conf = window.confirm($LL.MODERATOR.DENY_NAME_REQUEST_CONFIRM());
    if (!conf) return;
    const payload = {
      request_id: request.id,
    };
    const res = await fetch(`/api/registry/players/denyNameChange`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (res.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.DENY_NAME_REQUEST_FAILED()}: ${result['title']}`);
    }
  }
</script>

<PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
{#if name_requests.length}
  {$LL.MODERATOR.NAME_CHANGE_COUNT({ count: totalChanges })}
  <Table data={name_requests} let:item={request}>
    <colgroup slot="colgroup">
      <col class="country" />
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
      <th />
      <th>{$LL.COMMON.NAME()}</th>
      <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
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
        <Flag country_code={request.player_country} />
      </td>
      <td>
        <a href="/{$page.params.lang}/registry/players/profile?id={request.player_id}">
          <div class="flex">
            {request.old_name}
            <ArrowRight />
            {request.new_name}
          </div>
        </a>
      </td>
      <td class="mobile-hide">
        {new Date(request.date * 1000).toLocaleString($locale, options)}
      </td>
      {#if approval_status === 'pending'}
        <td>
          <ConfirmButton on:click={() => approveNameRequest(request)} />
          <CancelButton on:click={() => denyNameRequest(request)} />
        </td>
      {/if}
      {#if approval_status !== 'pending'}
        <td class="mobile-hide">
          {#if request.handled_by}
            <a href="/{$page.params.lang}/registry/players/profile?id={request.handled_by.id}">
              <div class="flex">
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
          <Button on:click={() => denyNameRequest(request)}>{$LL.COMMON.DELETE()}</Button>
        </td>
      {/if}
    </tr>
  </Table>
{:else}
  {$LL.MODERATOR.NO_PENDING_NAME_REQUESTS()}
{/if}
<PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />

<style>
  .flex {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 10px;
  }
  col.country {
    width: 10%;
  }
  col.name {
    width: 30%;
  }
  col.date {
    width: 20%;
  }
  col.approve {
    width: 25%;
  }
  col.handled-by {
    width: 15%;
  }
  col.delete {
    width: 25%;
  }
</style>
