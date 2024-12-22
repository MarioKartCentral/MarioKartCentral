<script lang="ts">
    import { onMount } from "svelte";
    import type { SessionMatch } from "$lib/types/account-matches";
    import Dialog from "../common/Dialog.svelte";
    import SessionMatchesDisplay from "./SessionMatchesDisplay.svelte";

    export let player_id: number;
    
    let matches: SessionMatch[] = [];
    let matches_dialog: Dialog;

    onMount(async() => {
        const res = await fetch(`/api/moderator/players/${player_id}/session_matches`);
        if(res.status === 200) {
            const body: SessionMatch[] = await res.json();
            matches = body;
        }
    });

    export function open() {
        matches_dialog.open();
    }
</script>

<Dialog bind:this={matches_dialog} header="Cookie Matches">
    <SessionMatchesDisplay {matches}/>
</Dialog>