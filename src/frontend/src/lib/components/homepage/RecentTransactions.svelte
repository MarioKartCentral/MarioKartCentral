<script lang="ts">
    import type { TeamTransfer } from "$lib/types/team-transfer";
    import { onMount } from "svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import { page } from "$app/stores";
    import TagBadge from "$lib/components/badges/TagBadge.svelte";
    import ArrowRight from "$lib/components/common/ArrowRight.svelte";
    import GameBadge from "$lib/components/badges/GameBadge.svelte";
    import ModeBadge from "$lib/components/badges/ModeBadge.svelte";
    import BaggerBadge from "$lib/components/badges/BaggerBadge.svelte";
    import LL from "$i18n/i18n-svelte";
    import HomeSection from "./HomeSection.svelte";

    export let style: string;
    let transfers: TeamTransfer[] = [];

    type TransferList = {
        transfers: TeamTransfer[];
        transfer_count: number;
        page_count: number;
    }
    
    async function fetchData() {
        let url = `/api/registry/teams/transfers/approved`;
        const res = await fetch(url);
        if (res.status !== 200) {
            return;
        }
        const body: TransferList = await res.json();
        transfers = body.transfers.slice(0, 6);
    }

    onMount(fetchData);
</script>

<HomeSection 
    header={$LL.HOMEPAGE.RECENT_TRANSACTIONS()} 
    link='/{$page.params.lang}/registry/teams/transfers' 
    linkText={$LL.HOMEPAGE.MORE_RECENT_TRANSACTIONS()}
    {style}
>
    {#if transfers.length}
        <div class="flex flex-col gap-[5px]">
            {#each transfers as transfer}
                <div class="row">
                    <div class="left">
                        <div class="flex items-center gap-[8px] mb-[5px] mt-[-5px]">
                            <div class="flag">
                                <Flag country_code={transfer.player_country_code}/>
                            </div>
                            <a href="/{$page.params.lang}/registry/players/profile?id={transfer.player_id}">
                                {transfer.player_name}
                                {#if transfer.is_bagger_clause}
                                    <BaggerBadge/>
                                {/if}
                            </a>
                        </div>
                        <div class="badges">
                            <GameBadge game={transfer.game} style='font-size: 0.95rem; width: 85px;' />
                            <ModeBadge mode={transfer.mode} style='font-size: 0.95rem; width: 85px;' />
                        </div>
                    </div>
                    <div class="right">
                        {#if transfer.roster_leave}
                            <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_leave.team_id}">
                                <TagBadge tag={transfer.roster_leave.roster_tag} color={transfer.roster_leave.team_color}/>
                            </a>
                            
                        {:else}
                            {$LL.TEAMS.TRANSFERS.NO_TEAM()}
                        {/if}
                        <ArrowRight/>
                        {#if transfer.roster_join}
                            <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_join.team_id}">
                                <TagBadge tag={transfer.roster_join.roster_tag} color={transfer.roster_join.team_color}/>
                            </a>
                        {:else}
                            {$LL.TEAMS.TRANSFERS.NO_TEAM()}
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</HomeSection>

<style>
    .row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        background-color: rgba(255, 255, 255, 0.15);
        padding: 12px;
    }
    .row:nth-child(odd) {
        background-color: rgba(210, 210, 210, 0.15);
    }
    .flag {
        zoom: 85%;
    }
    .right {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .badges {
        zoom: 85%;
    }
</style>