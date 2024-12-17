<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import LL from "$i18n/i18n-svelte";

    let from_player: PlayerInfo | null = null;
    let to_player: PlayerInfo | null = null;

    async function mergePlayers() {
        if(!from_player || !to_player) {
            return;
        }
        if(from_player.id == to_player.id) {
            alert($LL.MODERATOR.SELECT_UNIQUE_PLAYERS());
            return;
        }
        let conf = window.confirm($LL.MODERATOR.MERGE_PLAYERS_CONFIRM({old_player: from_player.name, new_player: to_player.name}));
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
            alert($LL.MODERATOR.MERGE_PLAYERS_SUCCESS());
            window.location.reload();
        } else {
            alert(`${$LL.MODERATOR.MERGE_PLAYERS_FAILED()}: ${result['title']}`);
        }
    }
</script>

<Section header={$LL.MODERATOR.MERGE_PLAYERS()}>
    <div class="option">
        <div>
            {$LL.MODERATOR.OLD_PLAYER()}:
        </div>
        <PlayerSearch bind:player={from_player}/>
    </div>
    
    {#if from_player}
        <div class="option">
            <div>
                {$LL.MODERATOR.NEW_PLAYER()}
            </div>
            <PlayerSearch bind:player={to_player}/>
        </div>
        
    {/if}
    {#if to_player}
        <Button on:click={mergePlayers}>{$LL.MODERATOR.MERGE_PLAYERS()}</Button>
    {/if}
</Section>

<style>
    div.option {
        margin-bottom: 10px;
    }
</style>