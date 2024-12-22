<script lang="ts">
    import type { SessionMatch } from "$lib/types/account-matches";
    import { locale } from "$i18n/i18n-svelte";
    import Flag from "../common/Flag.svelte";
    import { page } from "$app/stores";

    export let matches: SessionMatch[];

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };
</script>

<div class="container">
    {#each matches as match, i}
        <div class="row bg-{i%2}">
            <div class="header bg-primary-800">
                {match.users.length} accounts - {new Date(match.date * 1000).toLocaleString($locale, options)}
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
                    <div class="dates">
                        {new Date(user.date_earliest * 1000).toLocaleString($locale, options)}
                        -
                        {new Date(user.date_latest * 1000).toLocaleString($locale, options)}
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
    .dates {
        font-size: smaller;
        margin-left: 10px;
    }
</style>