<script lang="ts">
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import type { MyDiscord } from '$lib/types/my-discord';
    import { onMount } from 'svelte';
    import DiscordUser from './DiscordUser.svelte';

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
            alert(`An error occurred: ${result['title']}`);
        }
    }

    async function deleteDiscordData() {
        let conf = window.confirm("Are you sure you would like to delete your Discord data?");
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
            alert(`An error occurred: ${result['title']}`);
        }
    }
</script>

{#if user_info.id === null}
    Sign in or Register to link your Discord Account
{:else if linked_account !== undefined}
    {#if linked_account === null}
        <Button on:click={linkDiscord}>Link Discord Account</Button>
    {:else}
        <div class="flex">
            <DiscordUser discord={linked_account}/>
            <div class="section">
                <div class="flex buttons">
                    <div class="disc_button">
                        <Button size="xs" extra_classes="w-32" on:click={linkDiscord}>Relink account</Button>
                    </div>
                    <div class="disc_button">
                        <Button size="xs" extra_classes="w-32" on:click={deleteDiscordData}>Unlink account</Button>
                    </div>
                    <div class="disc_button">
                        <Button size="xs" extra_classes="w-32" on:click={refreshDiscordData}>Refresh</Button>
                    </div>
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