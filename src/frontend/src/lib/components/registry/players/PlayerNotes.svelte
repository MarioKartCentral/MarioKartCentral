<script lang="ts">
    import { page } from "$app/stores";
    import type { PlayerNotes } from "$lib/types/player-info";
    import LL from "$i18n/i18n-svelte";

    export let notes: PlayerNotes | null;

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };

</script>

<div>
    <h1 class="text-lg font-bold mb-1.5">{$LL.PLAYER_PROFILE.PLAYER_NOTES()}</h1>
    {#if notes}
        <div>{notes.notes}</div>
        <div class="text-sm text-slate-300 pt-1.5">
            {#if notes.edited_by}
                <a href="/{$page.params.lang}/registry/players/profile?id={notes.edited_by.id}" class="hover:text-yellow-300">{notes.edited_by.name}</a>
            {/if}
            {" - "}
            <span>{new Date(notes.date * 1000).toLocaleString($page.params.lang, options)}</span>
        </div>
    {:else}
        {$LL.NONE()}
    {/if}
</div>