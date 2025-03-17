<script lang="ts">
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import type { MyDiscord } from '$lib/types/my-discord';
    import { onMount } from 'svelte';
    import DiscordUser from './DiscordUser.svelte';
    import { permissions, check_permission } from '$lib/util/permissions';
    import LL from '$i18n/i18n-svelte';

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let linked_account: MyDiscord | null;

    onMount(async() => {
        const res = await fetch("/api/user/my_discord");
        if(res.status == 200) {
            const body: MyDiscord | null = await res.json();
            linked_account = body;
        }
    });

    async function linkDiscord() {
        let url = `/api/user/link_discord?page_url=${encodeURIComponent(window.location.href)}`;
        window.location.replace(url);
    }

    async function refreshDiscordData() {
        let endpoint = '/api/user/refresh_discord';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        const result = await response.json();
        if (response.status === 200) {
            linked_account = result;
        } else {
            alert(`${$LL.DISCORD.REFRESH_ERROR()}: ${result['title']}`);
        }
    }

    async function deleteDiscordData() {
        let conf = window.confirm($LL.DISCORD.DELETE_DATA_CONFIRM());
        if(!conf) return;
        let endpoint = '/api/user/delete_discord';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        const result = await response.json();
        if (response.status === 200) {
            linked_account = null;
        } else {
            alert(`${$LL.DISCORD.DELETE_DATA_ERROR()}: ${result['title']}`);
        }
    }

    async function syncDiscordAvatar() {
        const endpoint = '/api/user/sync_discord_avatar';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        const result = await response.json();
        if (response.status === 200) {
            window.location.reload(); // Refresh to show updated avatar
        } else {
            alert(`${$LL.DISCORD.SYNC_AVATAR_ERROR()}: ${result['title']}`);
        }
    }

</script>

{#if user_info.id === null}
    {$LL.DISCORD.SIGN_IN_REGISTER_TO_LINK()}
{:else if linked_account !== undefined}
    {#if linked_account === null}
        <Button on:click={linkDiscord} disabled={!check_permission(user_info, permissions.link_discord, true)}>{$LL.DISCORD.LINK_DISCORD()}</Button>
    {:else}
        <div class="flex">
            <DiscordUser discord={linked_account}/>
            <div class="section">
                <div class="flex buttons">
                    <div class="disc_button">
                        <Button size="xs" extra_classes="w-32" on:click={linkDiscord} disabled={!check_permission(user_info, permissions.link_discord, true)}>
                            {$LL.DISCORD.RELINK_DISCORD()}
                        </Button>
                    </div>
                    <div class="disc_button">
                        <Button size="xs" extra_classes="w-32" on:click={deleteDiscordData}>{$LL.DISCORD.UNLINK_DISCORD()}</Button>
                    </div>
                    <div class="disc_button">
                        <Button size="xs" extra_classes="w-32" on:click={refreshDiscordData} disabled={!check_permission(user_info, permissions.link_discord, true)}>
                            {$LL.DISCORD.REFRESH()}
                        </Button>
                    </div>
                    {#if linked_account.avatar}
                    <div class="disc_button">
                        <Button size="xs" extra_classes="w-32" on:click={syncDiscordAvatar}>
                            {$LL.DISCORD.SYNC_AVATAR()}
                        </Button>
                    </div>
                    {/if}
                </div>
            </div>
        </div>
    {/if}
{/if}

<style>
    div.flex {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
    }
    div.buttons {
        max-width: 500px;
    }
    div.section {
        margin: 5px 10px;
    }
    div.disc_button {
        margin: 3px;
    }
</style>