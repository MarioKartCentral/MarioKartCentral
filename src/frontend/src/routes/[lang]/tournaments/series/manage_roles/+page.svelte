<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import RoleInfo from "$lib/components/common/RoleInfo.svelte";
    import type { Role } from "$lib/types/role";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { get_highest_series_role_position } from "$lib/util/permissions";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import LL from "$i18n/i18n-svelte";

    let roles: Role[] = [];
    let series_id = 0;
    let selected_role: Role | null;

    let endpoint: string;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        series_id = Number(param_id);
        endpoint = `/api/tournaments/series/${series_id}`;
        const res = await fetch(`/api/tournaments/series/roles`);
        if(res.status === 200) {
            const body: Role[] = await res.json();
            roles = body;
            if(roles.length) {
                selected_role = roles[0];
            }
        }
    });
</script>

<Section header={$LL.TOURNAMENTS.SERIES.SERIES_ROLES()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/tournaments/series/details?id={series_id}">{$LL.TOURNAMENTS.SERIES.BACK_TO_SERIES()}</Button>
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
                <RoleInfo role={selected_role} url={endpoint} user_position={get_highest_series_role_position(user_info, series_id)}/>
            {/key}
        {/if}
    </div>
</Section>

<style>
    div.select {
        margin: auto;
        width: min-content;
    }
</style>