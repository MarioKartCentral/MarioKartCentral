<script lang="ts">
    import type { PlayerInfo } from "$lib/types/player-info";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import type { PlayerRoster } from "$lib/types/player-roster";
    import RosterSearch from "$lib/components/common/RosterSearch.svelte";
    import type { TeamRoster } from "$lib/types/team-roster";
    import Button from "$lib/components/common/buttons/Button.svelte";

    let player: PlayerInfo | null = null;
    let from_roster: PlayerRoster | null = null;
    let to_roster: TeamRoster | null = null;
    let is_bagger: boolean = false;

    $: is_bagger = from_roster ? from_roster.is_bagger_clause : is_bagger;

    function updateRosters () {
        if(!from_roster || !to_roster) {
            return;
        }
        if(from_roster.game !== to_roster.game) {
            to_roster = null;
        }
    }

    async function getPlayerRosters() {
        if(!player) {
            from_roster = null;
            to_roster = null;
            return;   
        }
        console.log(player);
        const url = `/api/registry/players/${player.id}`;
        const res = await fetch(url);
        if(res.status !== 200) {
            return;
        }
        const body: PlayerInfo = await res.json();
        player.rosters = body.rosters;
        player = player;
    }

    async function transferPlayer() {
        if(!player || !to_roster) {
            return;
        }
        const payload = {
            player_id: player.id,
            roster_id: to_roster.id,
            team_id: to_roster.team_id,
            roster_leave_id: from_roster ? from_roster.roster_id: null,
            is_bagger_clause: is_bagger
        };
        const endpoint = '/api/registry/teams/forceTransferPlayer';
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        console.log(payload);
        const result = await res.json();
        if (res.status < 300) {
            alert(`Successfully transferred ${player.name} to ${to_roster.name}`);
            window.location.reload();
        } else {
            alert(`Transferring player failed: ${result['title']}`);
        }
    }
</script>

<PlayerSearch bind:player={player} on:change={getPlayerRosters}/>
{#if player}
    <div class="transfer">
        <div class="item">
            <div>Old Roster</div>
            <div>
                <select bind:value={from_roster} name="from" on:change={updateRosters}>
                    <option value={null}>
                        None
                    </option>
                    {#each player.rosters as roster}
                        <option value={roster}>
                            {roster.roster_name}
                            ({roster.game.toUpperCase()})
                            {#if roster.is_bagger_clause}
                                (Bagger)
                            {/if}
                        </option>
                    {/each}
                </select>
            </div>
        </div>
        <div class="item">
            <div>New Roster</div>
            {#key from_roster}
                <RosterSearch bind:roster={to_roster} game={from_roster?.game}/>
            {/key}
        </div>
        {#if !from_roster && to_roster?.game === "mkw"}
            <div class="item">
                <div>Bagger?</div>
                <div>
                    <select bind:value={is_bagger}>
                        <option value={false} selected>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
        {/if}
        {#if to_roster}
            <Button on:click={transferPlayer}>Transfer</Button>
        {/if}
    </div>
    
{/if}

<style>
    .item {
        margin: 10px 0;
    }
</style>