<script lang="ts">
    import type { Role } from "$lib/types/role";
    import type { RoleInfo } from "$lib/types/role";
    import { onMount } from "svelte";
    import Table from "$lib/components/common/Table.svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import { page } from "$app/stores";
    import { CloseSolid } from "flowbite-svelte-icons";

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
        <div class="table">
            <Table>
                <col class="country"/>
                <col class="name"/>
                <col class="remove"/>
                <tbody>
                    {#each role_info.players as player}
                    <tr>
                        <td><Flag country_code={player.country_code}/></td>
                        <td>
                            <a href="/{$page.params.lang}/registry/players/profile?id={player.id}">
                                {player.name}
                            </a>
                        </td>
                        <td style="text-align:right;">
                            <div class="close">
                                <CloseSolid/>
                            </div>
                        </td>
                    </tr>
                    {/each}
                </tbody>
                
            </Table>
        </div>
    {/if}
</div>

<style>
    div.table {
        margin: auto;
        min-width: 50%;
    }
    col.country {
        width: 15%;
    }
    col.name {
        width: 50%;
    }
    col.remove {
        width: 35%;
    }
    .close {
        display: flex;
        flex-direction: row-reverse;
        padding-right: 10px;
    }
</style>