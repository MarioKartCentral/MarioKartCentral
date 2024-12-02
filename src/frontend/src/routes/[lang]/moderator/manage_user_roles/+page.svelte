<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { Role } from "$lib/types/role";
    import { onMount } from "svelte";
    import { get_highest_role_position } from "$lib/util/permissions";
    import RoleInfo from "$lib/components/common/RoleInfo.svelte";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { permissions, check_permission } from "$lib/util/permissions";
    import LL from "$i18n/i18n-svelte";

    let roles: Role[] = [];
    let selected_role: Role | null;

    let endpoint = "/api";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        const res = await fetch('/api/roles');
        if(res.status === 200) {
            const body: Role[] = await res.json();
            roles = body;
            if(roles.length) {
                selected_role = roles[0];
            }
        }
    });
</script>

{#if check_permission(user_info, permissions.manage_user_roles)}
    <Section header={$LL.ROLES.USER_ROLES()}>
        {#if roles.length}
            <div class="select">
                <select bind:value={selected_role}>
                    {#each roles as role}
                        <option value={role}>{role.name}</option>
                    {/each}
                </select>
            </div>
        {/if}
        <div>
            {#if selected_role}
                {#key selected_role}
                    <RoleInfo role={selected_role} url={endpoint} user_position={get_highest_role_position(user_info)}/>
                {/key}
            {/if}
        </div>
    </Section>
{:else}
    {$LL.NO_PERMISSION()}
{/if}


<style>
    div.select {
        margin: auto;
        width: min-content;
    }
</style>