<script lang="ts">
    import type { PlayerInfo } from "$lib/types/player-info";
    import Section from "$lib/components/common/Section.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

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
            alert("Successfully sent a claim for this player to staff!");
            window.location.reload();
        }
        else {
            alert(`Claiming player failed: ${result['title']}`);
        }
    }
</script>

<Section header="Claim Player">
    <div>
        This is an unclaimed player, meaning that this player has participated in past tournaments, but does not have a user account at Mario Kart Central.
        To request to claim this player, click the button below.
    </div>
    <div class="claim-button">
        <Button on:click={claimPlayer}>Claim Player</Button>
    </div>
    
</Section>

<style>
    .claim-button {
        margin-top: 10px;
    }
</style>