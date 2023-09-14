<script lang="ts">
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";

    export let permission: string;

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });
</script>

{#if user_info.is_checked}
    {#if user_info.permissions.includes(permission)}
        <slot/>
    {:else}
        You do not have permission to view this page.
    {/if}
{/if}