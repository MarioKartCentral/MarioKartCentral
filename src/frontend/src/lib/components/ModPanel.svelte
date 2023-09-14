<script lang="ts">
    import DropdownMenu from "./DropdownMenu.svelte";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from "$lib/types/user-info";
    import { permissions } from "$lib/util/util";
    import { page } from '$app/stores';

    let dropdown: DropdownMenu;
    export function toggleModPanel() {
        dropdown.toggleDropdown();
    }

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });
</script>

<DropdownMenu bind:this={dropdown}>
    {#if user_info.permissions.includes(permissions.manage_teams)}
        <div>
            <a href="/{$page.params.lang}/moderator/approve_teams">Approve Teams</a>
        </div>
    {/if}
</DropdownMenu>
