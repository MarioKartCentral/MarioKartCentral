<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";

    let player: PlayerInfo | null = null;
</script>

<svelte:head>
    <title>Transfer Account | Mario Kart Central</title>
</svelte:head>
<Section header="Transfer Account from Old MKC Site">
    <div>
        You can search for your info here and transfer your account from the old site to the new site. Alternatively, you can log in with the email linked to your account on the old site and it will automatically transfer your account.
    </div>
    <div>
        <PlayerSearch has_connected_user={false} bind:player={player}/>
    </div>
    {#if player}
        <div>
            <Button>Transfer Account</Button>
        </div>
    {/if}
</Section>

<style>
    div {
        margin-bottom: 10px;
    }
</style>