<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import RoleInfo from "$lib/components/common/RoleInfo.svelte";
    import type { Role } from "$lib/types/role";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { get_highest_team_role_position } from "$lib/util/permissions";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { check_permission, team_permissions } from "$lib/util/permissions";
    import LL from "$i18n/i18n-svelte";

    let roles: Role[] = [];
    let team_id = 0;
    let selected_role: Role | null;

    let endpoint: string;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        team_id = Number(param_id);
        endpoint = `/api/registry/teams/${team_id}`;

        // get list of team roles
        const res = await fetch(`/api/registry/teams/roles`);
        if(res.status === 200) {
            const body: Role[] = await res.json();
            roles = body;
            if(roles.length) {
                selected_role = roles[0];
            }
        }
    });
</script>

{#if check_permission(user_info, team_permissions.manage_team_roles)}
    <Section header={$LL.TEAMS.EDIT.TEAM_ROLES()}>
        <div slot="header_content">
            <Button href="/{$page.params.lang}/registry/teams/profile?id={team_id}">Back to Team</Button>
        </div>
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
                    <RoleInfo role={selected_role} url={endpoint} user_position={get_highest_team_role_position(user_info, team_id)}/>
                {/key}
            {/if}
        </div>
    </Section>
{:else}
    {$LL.COMMON.NO_PERMISSION()}
{/if}


<style>
    div.select {
        margin: auto;
        width: min-content;
    }
</style>