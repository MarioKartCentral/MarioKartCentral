<script lang="ts">
    import type { AltFlag } from "$lib/types/alt-flag";
    import Dialog from "../common/Dialog.svelte";
    import { onMount } from "svelte";
    import AltFlags from "./AltFlags.svelte";
    import LL from "$i18n/i18n-svelte";

    export let player_id: number;

    let alt_dialog: Dialog;
    let flags: AltFlag[] = [];

    export function open() {
        alt_dialog.open();
    }

    onMount(async() => {
        const res = await fetch(`/api/moderator/playerAltFlags?player_id=${player_id}`);
        if(res.status === 200) {
            const body: AltFlag[] = await res.json();
            console.log(body);
            flags = body;
        }
    });
</script>

<Dialog bind:this={alt_dialog} header={$LL.MODERATOR.ALT_DETECTION.PLAYER_ALT_FLAGS()}>
    <AltFlags {flags}/>
</Dialog>