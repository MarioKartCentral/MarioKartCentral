<script lang="ts">
    import Button from "$lib/components/common/buttons/Button.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import type { User } from "$lib/types/user";
    import { onMount } from "svelte";
    import PageNavigation from "$lib/components/common/PageNavigation.svelte";
    import Table from "$lib/components/common/Table.svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import { page } from "$app/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import LL from "$i18n/i18n-svelte";
    import { check_permission, permissions } from "$lib/util/permissions";

    let users: User[] = [];
    let total_users = 0;
    let total_pages = 0;
    let current_page = 1;
    let name_or_email = "";

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    async function fetchData() {
        let url = `/api/user/list?page=${current_page}`;
        if(name_or_email) {
            url += `&name_or_email=${name_or_email}`;
        }
        const res = await fetch(url);
        if(res.status === 200) {
            const body = await res.json();
            users = body['users'];
            total_users = body['user_count'];
            total_pages = body['page_count'];
        }
    }

    async function search() {
        current_page = 1;
        fetchData();
    }

    onMount(fetchData);
</script>

{#if check_permission(user_info, permissions.edit_user)}
    <Section header={$LL.MODERATOR.MANAGE_USERS.SEARCH_FOR_USERS()}>
        <div class="flex">
            <form on:submit|preventDefault={search}>
                <input bind:value={name_or_email} placeholder={$LL.MODERATOR.MANAGE_USERS.SEARCH_BY_NAME_EMAIL()}/>
                <Button type="submit">{$LL.COMMON.SEARCH()}</Button>
            </form>
            
        </div>
        <div class="user_list">
            {$LL.MODERATOR.MANAGE_USERS.USER_COUNT({count: total_users})}
            <PageNavigation bind:currentPage={current_page} bind:totalPages={total_pages} refresh_function={fetchData}/>
            {#if total_users}
                <Table>
                    <col class="id"/>
                    <col class="email"/>
                    <col class="country"/>
                    <col class="name"/>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>{$LL.LOGIN.EMAIL()}</th>
                            <th/>
                            <th>{$LL.COMMON.PLAYER()}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each users as u, i}
                            <tr class="row-{i % 2}">
                                <td>
                                    <a href="/{$page.params.lang}/moderator/users/edit?id={u.id}">
                                        {u.id}
                                    </a>
                                </td>
                                <td>
                                    <a href="/{$page.params.lang}/moderator/users/edit?id={u.id}">
                                        {u.email}
                                    </a>
                                </td>
                                <td>
                                    {#if u.player}
                                        <Flag country_code={u.player.country_code}/>
                                    {/if}
                                </td>
                                <td>
                                    {#if u.player}
                                        <a href="/{$page.params.lang}/registry/players/profile?id={u.player.id}">
                                            {u.player.name}
                                        </a>
                                    {/if}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </Table>
            {/if}
        </div>
    </Section>
{:else}
    {$LL.COMMON.NO_PERMISSION()}
{/if}


<style>
    .flex {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 5px;
    }
    input {
        width: 400px;
    }
    .user_list {
        margin-top: 10px;
    }
    col.id {
        width: 10%;
    }
    col.email {
        width: 45%;
    }
    col.country {
        width: 5%;
    }
    col.name {
        width: 40%;
    }
</style>