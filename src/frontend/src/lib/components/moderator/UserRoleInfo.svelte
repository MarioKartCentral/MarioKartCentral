<script lang="ts">
    import type { Role } from "$lib/types/role";
    import type { RoleInfo } from "$lib/types/role";
    import { onMount } from "svelte";
    import Table from "$lib/components/common/Table.svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import { page } from "$app/stores";
    import { CloseSolid } from "flowbite-svelte-icons";
    import { get_highest_role_position } from "$lib/util/permissions";
    import type { PlayerInfo } from "$lib/types/player-info";
    import PlayerSearch from "../common/PlayerSearch.svelte";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CancelButton from "../common/buttons/CancelButton.svelte";
    import type { Player } from "$lib/types/player";

    export let role: Role;
    let role_info: RoleInfo;

    let selected_player: PlayerInfo | null = null;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        await loadInfo();
    });

    async function loadInfo() {
        const res = await fetch(`/api/roles/${role.id}`);
        if(res.status === 200) {
            const body: RoleInfo = await res.json();
            selected_player = null;
            role_info = body;
        }
    }

    async function giveRoleToPlayer(player_id: number) {
        const payload = {
            player_id: player_id,
            role_name: role.name
        };
        const endpoint = `/api/roles/grant`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            await loadInfo();
        } else {
            alert(`Failed to add role: ${result['title']}`);
        }
    }

    async function removeRoleFromPlayer(player: Player) {
        let conf = window.confirm(`Are you sure you want to remove the role ${role.name} from ${player.name}?`);
        if(!conf) return;
        const payload = {
            player_id: player.id,
            role_name: role.name
        };
        const endpoint = `/api/roles/remove`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            await loadInfo();
        } else {
            alert(`Failed to remove role: ${result['title']}`);
        }
    }
</script>

<div>
    {#if role_info}
        <div class="role">
            {#if get_highest_role_position(user_info) < role.position}
                <div>
                    Add Player
                </div>
                <div class="addplayer">
                    <PlayerSearch bind:player={selected_player}/>
                    {#if selected_player !== null}
                        <Button on:click={() => giveRoleToPlayer(Number(selected_player?.id))}>Add</Button>
                    {/if}
                </div>
            {:else}
                <div>
                    You do not have permission to edit this role.
                </div>
            {/if}
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
                                {#if get_highest_role_position(user_info) < role.position}
                                    <div class="close">
                                        <CancelButton on:click={() => removeRoleFromPlayer(player)}/>
                                    </div>
                                {/if}
                            </td>
                        </tr>
                        {/each}
                    </tbody>
                </Table>
            </div>
        </div>
    {/if}
</div>

<style>
    div.role {
        display: flex;
        margin-top: 10px;
        text-align: center;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    div.addplayer {
        display: flex;
        gap: 10px;
    }
    div.table {
        display: table;
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