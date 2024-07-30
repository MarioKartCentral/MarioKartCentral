<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import SeriesRoleInfo from "$lib/components/tournaments/series/SeriesRoleInfo.svelte";
    import type { Role } from "$lib/types/role";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";

    let roles: Role[] = [];
    let id = 0;
    let selected_role: Role | null;

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);
        const res = await fetch('/api/tournaments/series/roles');
        if(res.status === 200) {
            const body: Role[] = await res.json();
            roles = body;
            if(roles.length) {
                selected_role = roles[0];
            }
        }
    });
</script>

<Section header="Series Roles">
    <div slot="header_content">
        <Button href="/{$page.params.lang}/tournaments/series/details?id={id}">Back to Series</Button>
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
                <SeriesRoleInfo role={selected_role} series_id={id}/>
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