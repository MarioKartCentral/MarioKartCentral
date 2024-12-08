<script lang="ts">
    import type { PlayerInfo } from "$lib/types/player-info";
    import Section from "$lib/components/common/Section.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import LL from "$i18n/i18n-svelte";

    export let player: PlayerInfo;

    async function claimPlayer() {
        const payload = {
            player_id: player.id
        };
        const endpoint = '/api/registry/players/claim';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            alert($LL.SHADOW_PLAYERS.CLAIM_PLAYER_SUCCESS());
            window.location.reload();
        }
        else {
            alert(`${$LL.SHADOW_PLAYERS.CLAIM_PLAYER_FAILED()}: ${result['title']}`);
        }
    }
</script>

<Section header={$LL.SHADOW_PLAYERS.CLAIM_PLAYER()}>
    <div>
        {$LL.SHADOW_PLAYERS.UNCLAIMED_PLAYER_DESCRIPTION()}
    </div>
    <div class="claim-button">
        <Button on:click={claimPlayer}>{$LL.SHADOW_PLAYERS.CLAIM_PLAYER()}</Button>
    </div>
    
</Section>

<style>
    .claim-button {
        margin-top: 10px;
    }
</style>