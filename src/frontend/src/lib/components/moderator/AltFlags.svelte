<script lang="ts">
    import Table from "../common/Table.svelte";
    import LL from "$i18n/i18n-svelte";
    import type { AltFlag } from "$lib/types/alt-flag";
    import { page } from "$app/stores";
    import Flag from "../common/Flag.svelte";
    import { locale } from "$i18n/i18n-svelte";

    export let flags: AltFlag[];

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };
</script>

<Table>
    <col class="players">
    <col class="type">
    <col class="score">
    <col class="data mobile-hide">
    <col class="date mobile-hide">
    <thead>
        <tr>
            <th>{$LL.MODERATOR.ALT_DETECTION.TABLE.PLAYERS()}</th>
            <th>{$LL.MODERATOR.ALT_DETECTION.TABLE.TYPE()}</th>
            <th>{$LL.MODERATOR.ALT_DETECTION.TABLE.SCORE()}</th>
            <th class="mobile-hide">{$LL.MODERATOR.ALT_DETECTION.TABLE.DATA()}</th>
            <th class="mobile-hide">{$LL.MODERATOR.ALT_DETECTION.TABLE.DETECTED_AT()}</th>
        </tr>
    </thead>
    <tbody>
        {#each flags as flag}
            <tr>
                <td>
                    {#each flag.players as player}
                        <a href="/{$page.params.lang}/registry/players/profile?id={player.id}">
                            <div class="player-name">
                                <Flag country_code={player.country_code}/>
                                {player.name}
                            </div>
                        </a>
                    {/each}
                </td>
                <td>
                    {flag.type}
                </td>
                <td>
                    {flag.score}
                </td>
                <td class="mobile-hide">
                    {flag.data}
                </td>
                <td class="mobile-hide">
                    {new Date(flag.date * 1000).toLocaleString($locale, options)}
                </td>
            </tr>
        {/each}
    </tbody>
</Table>

<style>
    col.players {
        width: 30%;
    }
    col.type {
        width: 10%;
    }
    col.score {
        width: 10%;
    }
    col.data {
        width: 30%;
    }
    col.date {
        width: 20%;
    }
    .player-name {
        display: flex;
        gap: 10px;
        align-items: center;
    }
</style>