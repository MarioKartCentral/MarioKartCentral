<script lang="ts">
    import type { Role } from "$lib/types/role";
    import type { RoleInfo } from "$lib/types/role";
    import { onMount } from "svelte";

    export let role: Role;
    let role_info: RoleInfo;

    onMount(async() => {
        const res = await fetch(`/api/roles/${role.id}`);
        if(res.status === 200) {
            const body: RoleInfo = await res.json();
            role_info = body;
        }
    });
</script>

<div>
    {#if role_info}
        {#each role_info.players as player}
            <div>{player.name}</div>
        {/each}
    {/if}
</div>