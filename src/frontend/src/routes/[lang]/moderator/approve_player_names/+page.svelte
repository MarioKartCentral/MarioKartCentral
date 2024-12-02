<script lang="ts">
    import { onMount } from "svelte";
    import type { PlayerNameChangeRequest } from "$lib/types/player-name-change-request";
    import { check_permission, permissions } from "$lib/util/permissions";
    import type { UserInfo } from '$lib/types/user-info';
    import { user } from '$lib/stores/stores';
    import Table from "$lib/components/common/Table.svelte";
    import { page } from "$app/stores";
    import ArrowRight from "$lib/components/common/ArrowRight.svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import { locale } from "$i18n/i18n-svelte";
    import ConfirmButton from "$lib/components/common/buttons/ConfirmButton.svelte";
    import CancelButton from "$lib/components/common/buttons/CancelButton.svelte";
    import LL from "$i18n/i18n-svelte";

    let name_requests: PlayerNameChangeRequest[] = [];

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async () => {
        const res = await fetch(`/api/registry/players/pendingNameChanges`);
        if (res.status === 200) {
            const body: PlayerNameChangeRequest[] = await res.json();
            name_requests = body;
        }
    });

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };

    async function approveNameRequest(request: PlayerNameChangeRequest) {
        let conf = window.confirm($LL.MODERATOR.APPROVE_NAME_REQUEST_CONFIRM());
        if(!conf) return;
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
        if(!conf) return;
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

{#if check_permission(user_info, permissions.edit_player)}
<Section header={$LL.MODERATOR.PENDING_NAME_REQUESTS()}>
    {#if name_requests.length}
        <Table>
            <col class="country">
            <col class="name">
            <col class="date">
            <col class="approve">
            <thead>
                <tr>
                    <th/>
                    <th>{$LL.NAME()}</th>
                    <th>{$LL.DATE()}</th>
                    <th>{$LL.MODERATOR.APPROVE()}</th>
                </tr>
            </thead>
            <tbody>
                {#each name_requests as r, i}
                    <tr class="row-{i % 2}">
                        <td>
                            <Flag country_code={r.player_country}/>
                        </td>
                        <td>
                            <a href="/{$page.params.lang}/registry/players/profile?id={r.player_id}">
                                <div class="flex">
                                    {r.player_name}
                                    <ArrowRight/>
                                    {r.request_name}
                                </div>
                            </a>
                        </td>
                        <td>
                            {new Date(r.date * 1000).toLocaleString($locale, options)}
                        </td>
                        <td>
                            <ConfirmButton on:click={() => approveNameRequest(r)}/>
                            <CancelButton on:click={() => denyNameRequest(r)}/>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </Table>
    {:else}
        {$LL.MODERATOR.NO_PENDING_NAME_REQUESTS()}
    {/if}
</Section>
{:else}
    {$LL.NO_PERMISSION()}
{/if}

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
      width: 40%;
    }
    col.date {
      width: 25%;
    }
    col.approve {
      width: 25%;
    }
  </style>