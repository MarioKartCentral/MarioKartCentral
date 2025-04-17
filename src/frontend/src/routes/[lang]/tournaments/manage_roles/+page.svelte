<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import RoleInfo from "$lib/components/common/RoleInfo.svelte";
    import type { Role } from "$lib/types/role";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { get_highest_tournament_role_position } from "$lib/util/permissions";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import type { Tournament } from "$lib/types/tournament";
    import LL from "$i18n/i18n-svelte";
    import { check_tournament_permission, tournament_permissions } from "$lib/util/permissions";

    let roles: Role[] = [];
    let tournament_id = 0;
    let selected_role: Role | null;

    let endpoint: string;
    let series_id: number | null;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        tournament_id = Number(param_id);
        endpoint = `/api/tournaments/${tournament_id}`;
        // get series ID from tournament ID
        const res1 = await fetch(`/api/tournaments/${tournament_id}`);
        if(res1.status === 200) {
            const body: Tournament = await res1.json();
            series_id = body.series_id;
        }

        // get list of tournament roles
        const res2 = await fetch(`/api/tournaments/roles`);
        if(res2.status === 200) {
            const body: Role[] = await res2.json();
            roles = body;
            if(roles.length) {
                selected_role = roles[0];
            }
        }
    });
</script>

{#if user_info.is_checked}
    {#if check_tournament_permission(user_info, tournament_permissions.manage_tournament_roles, tournament_id, series_id)}
        <Section header={$LL.TOURNAMENTS.TOURNAMENT_ROLES()}>
            <div slot="header_content">
                <Button href="/{$page.params.lang}/tournaments/details?id={tournament_id}">{$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}</Button>
            </div>
            {#if roles.length}
                <div class="select">
                    <select bind:value={selected_role}>
                        {#each roles.toSorted((a, b) => a.position - b.position) as role}
                            <option value={role}>{role.name}</option>
                        {/each}
                    </select>
                </div>
            {/if}
            <div>
                {#if selected_role}
                    {#key selected_role}
                        <RoleInfo role={selected_role} url={endpoint} user_position={get_highest_tournament_role_position(user_info, tournament_id, series_id)}/>
                    {/key}
                {/if}
            </div>
        </Section>
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}

<style>
    div.select {
        margin: auto;
        width: min-content;
    }
</style>