<script lang="ts">
    import { onMount } from "svelte";
    import type { SessionMatch, IPMatch } from "$lib/types/account-matches";
    import Dialog from "../common/Dialog.svelte";
    import SessionMatchesDisplay from "./SessionMatchesDisplay.svelte";
    import IPMatchesDisplay from "./IPMatchesDisplay.svelte";
    import LL from "$i18n/i18n-svelte";

    export let player_id: number;
    
    let session_matches: SessionMatch[] = [];
    let ip_matches: IPMatch[] = [];
    let matches_dialog: Dialog;

    onMount(async() => {
        const res = await fetch(`/api/moderator/players/${player_id}/session_matches`);
        if(res.status === 200) {
            const body: SessionMatch[] = await res.json();
            session_matches = body;
        }
        const res2 = await fetch(`/api/moderator/players/${player_id}/ip_matches`);
        if(res2.status === 200) {
            const body: IPMatch[] = await res2.json();
            ip_matches = body;
        }
    });

    export function open() {
        matches_dialog.open();
    }
</script>

<Dialog bind:this={matches_dialog} header={$LL.MODERATOR.ALT_DETECTION.ACCOUNT_MATCHES()}>
    <div class="section">
        <div class="heading">
            {$LL.MODERATOR.ALT_DETECTION.SESSION_MATCHES()}
        </div>
        {#if session_matches.length}
            <SessionMatchesDisplay matches={session_matches}/>
        {:else}
            {$LL.MODERATOR.ALT_DETECTION.NO_ACCOUNT_MATCHES()}
        {/if}
        
    </div>
    <div class="section">
        <div class="heading">
            {$LL.MODERATOR.ALT_DETECTION.IP_MATCHES()}
        </div>
        {#if ip_matches.length}
            <IPMatchesDisplay matches={ip_matches}/>
        {:else}
        {$LL.MODERATOR.ALT_DETECTION.NO_ACCOUNT_MATCHES()}
        {/if}
        
    </div>
    
</Dialog>

<style>
    .heading {
        font-size: large;
        font-weight: bold;
    }
    .section {
        margin-bottom: 10px;
    }
</style>