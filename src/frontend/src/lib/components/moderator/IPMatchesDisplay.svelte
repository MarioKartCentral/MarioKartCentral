<script lang="ts">
    import type { IPMatch } from "$lib/types/account-matches";
    import { locale } from "$i18n/i18n-svelte";
    import Flag from "../common/Flag.svelte";
    import { page } from "$app/stores";
    import LL from "$i18n/i18n-svelte";

    export let matches: IPMatch[];

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };
</script>

<div class="container">
    {#each matches as match, i}
        <div class="row bg-{i%2}">
            <div class="header bg-primary-800">
                {$LL.MODERATOR.ALT_DETECTION.ACCOUNT_COUNT({count:match.users.length})} -
                {#if match.ip_address}
                    <a href="https://whatismyipaddress.com/ip/{match.ip_address}" class="underline">
                        {match.ip_address}
                    </a>
                    -
                {/if}
                {new Date(match.date * 1000).toLocaleString($locale, options)}
            </div>
            {#each match.users as user}
                <div class="flex">
                    <div class="player_name">
                        <span>
                            <Flag country_code={user.player_info.country_code}/>
                        </span>
                        <span class={user.is_banned ? 'banned-name' : ''}>
                            <a href="/{$page.params.lang}/registry/players/profile?id={user.player_info.id}">
                                {user.player_info.name}
                            </a>
                        </span>
                    </div>
                    <div class="date_times">
                        {new Date(user.date_earliest * 1000).toLocaleString($locale, options)}
                        -
                        {new Date(user.date_latest * 1000).toLocaleString($locale, options)}
                    </div>
                    <div class="date_times">
                        {$LL.MODERATOR.ALT_DETECTION.NUMBER_TIMES_LOGGED_IN({count: user.times})}
                    </div>
                </div>
            {/each}
        </div>
    {/each}
</div>


<style>
    .container {
        margin-top: 5px;
    }
    .row {
        margin-top: 5px;
        margin-left: 5px;
        margin-right: 5px;
    }
    .header {
        font-weight: bold;
        padding: 5px;
    }
    .flex {
        padding: 5px;
        align-items: center;
        flex-wrap: wrap;
    }
    .bg-0 {
        background-color: rgba(255, 255, 255, 0.15);
    }
    .bg-1 {
        background-color: rgba(255, 255, 255, 0.25);
    }
    .player_name {
        min-width: 150px;
    }
    .banned_name {
        opacity: 0.7;
        text-decoration: line-through;
    }
    .date_times {
        font-size: smaller;
        min-width: 250px;
        margin-left: 10px;
    }
</style>