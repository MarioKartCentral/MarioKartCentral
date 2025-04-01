<script lang="ts">
    import LoginRegister from "$lib/components/login/LoginRegister.svelte";
    import type { UserInfo } from '$lib/types/user-info';
    import { user } from '$lib/stores/stores';
    import { page } from "$app/stores";
    import LL from "$i18n/i18n-svelte";

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });
</script>

<svelte:head>
    <title>Login | Mario Kart Central</title>
</svelte:head>

{#if !user_info.id}
    <LoginRegister send_to="/{$page.params.lang}/"/>
{:else}
    {$LL.LOGIN.ALREADY_LOGGED_IN()}
{/if}