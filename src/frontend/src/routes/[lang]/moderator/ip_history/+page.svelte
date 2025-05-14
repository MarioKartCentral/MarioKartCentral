<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import type { IPHistory } from "$lib/types/ip-addresses";
    import { check_permission, permissions } from "$lib/util/permissions";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import Section from "$lib/components/common/Section.svelte";
    import LL from "$i18n/i18n-svelte";
    import PlayerName from "$lib/components/common/PlayerName.svelte";
    import IpInfo from "$lib/components/moderator/IPInfo.svelte";
    import { locale } from "$i18n/i18n-svelte";

    let history: IPHistory;

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        if(param_id) {
            const res = await fetch(`/api/moderator/ip_addresses/${param_id}`);
            if(res.status === 200) {
                const body: IPHistory = await res.json();
                history = body;
            }
        }
    });

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };
</script>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.view_basic_ip_info)}
        {#if history}
            <Section header={$LL.MODERATOR.ALT_DETECTION.IP_HISTORY()}>
                {#if history.history.length}
                    <IpInfo ip={history.history[0].time_range.ip_address}/>
                {/if}
                {#each history.history as p}
                    <div class="history-container">
                        <div>
                            {#if p.player}
                                <PlayerName player={p.player}/>
                            {:else}
                                User ID {p.time_range.user_id}
                            {/if}
                        </div>
                        <div>
                            {new Date(p.time_range.date_earliest * 1000).toLocaleString($locale, options)}
                            -
                            {new Date(p.time_range.date_earliest * 1000).toLocaleString($locale, options)}
                        </div>
                        <div>
                            {$LL.MODERATOR.ALT_DETECTION.NUM_TIMES({"count": p.time_range.times})}
                        </div>
                    </div> 
                {/each}
            </Section>
        {/if}
        
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}

<style>
    .history-container {
        margin-top: 10px;
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        background-color: rgba(255, 255, 255, 0.15);
        padding: 0px 10px;
        align-items: center;
        min-height: 45px;
    }
</style>