<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

    let from_player: PlayerInfo | null = null;
    let to_player: PlayerInfo | null = null;

    async function mergePlayers() {
        if(!from_player || !to_player) {
            return;
        }
        if(from_player.id == to_player.id) {
            alert("Please select two different players");
            return;
        }
        let conf = window.confirm(`Are you sure you want to merge all of ${from_player.name}'s data into ${to_player.name}? This will DELETE ${from_player.name} completely.`);
        if(!conf) return;
        const payload = {
            from_player_id: from_player.id,
            to_player_id: to_player.id,
        };
        const endpoint = "/api/registry/players/merge";
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (res.status < 300) {
            alert('Successfully merged players!');
            window.location.reload();
        } else {
            alert(`Merging players failed: ${result['title']}`);
        }
    }
</script>

<Section header="Merge Players">
    <div class="option">
        <div>
            Old Player:
        </div>
        <PlayerSearch bind:player={from_player}/>
    </div>
    
    {#if from_player}
        <div class="option">
            <div>New Player:</div>
            <PlayerSearch bind:player={to_player}/>
        </div>
        
    {/if}
    {#if to_player}
        <Button on:click={mergePlayers}>Merge Players</Button>
    {/if}
</Section>

<style>
    div.option {
        margin-bottom: 10px;
    }
</style>