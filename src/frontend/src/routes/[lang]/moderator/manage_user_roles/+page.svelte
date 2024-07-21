<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import UserRoleInfo from "$lib/components/moderator/UserRoleInfo.svelte";
    import type { Role } from "$lib/types/role";
    import { onMount } from "svelte";

    let roles: Role[] = [];
    let selected_role: Role | null;

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

<Section header="User Roles">
    <div>
        {#if roles.length}
            <select bind:value={selected_role}>
                {#each roles as role}
                    <option value={role}>{role.name}</option>
                {/each}
            </select>
        {/if}
    </div>
    <div>
        {#if selected_role}
            {#key selected_role}
                <UserRoleInfo role={selected_role}/>
            {/key}
        {/if}
    </div>
</Section>