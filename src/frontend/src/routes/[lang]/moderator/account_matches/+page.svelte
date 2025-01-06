<script lang="ts">
    import { onMount } from "svelte";
    import { check_permission, permissions } from "$lib/util/permissions";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import LL from "$i18n/i18n-svelte";
    import type { SessionMatch, SessionMatchList, IPMatch, IPMatchList } from "$lib/types/account-matches";
    import PageNavigation from "$lib/components/common/PageNavigation.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import SessionMatchesDisplay from "$lib/components/moderator/SessionMatchesDisplay.svelte";
    import IPMatchesDisplay from "$lib/components/moderator/IPMatchesDisplay.svelte";

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });
    
    let session_matches: SessionMatch[] = [];
    let total_session_matches = 0;
    let total_session_pages = 0;
    let current_session_page = 1;

    let ip_matches: IPMatch[] = [];
    let total_ip_matches = 0;
    let total_ip_pages = 0;
    let current_ip_page = 1;

    async function fetchSessionData() {
        const res = await fetch(`/api/moderator/session_matches?page=${current_session_page}`);
        if(res.status === 200) {
            const body: SessionMatchList = await res.json();
            session_matches = body.session_matches;
            total_session_matches = body.match_count;
            total_session_pages = body.page_count;
        }
    }

    async function fetchIPData() {
        const res = await fetch(`/api/moderator/ip_matches?page=${current_ip_page}`);
        if(res.status === 200) {
            const body: IPMatchList = await res.json();
            ip_matches = body.ip_matches;
            total_ip_matches = body.match_count;
            total_ip_pages = body.page_count;
        }
    }

    onMount(async() => {
        fetchSessionData();
        fetchIPData();
    });
</script>

{#if check_permission(user_info, permissions.view_account_matches)}
    <Section header={$LL.MODERATOR.ALT_DETECTION.SESSION_MATCHES()}>
        {#if total_session_matches}
            {$LL.MODERATOR.ALT_DETECTION.ACCOUNT_MATCH_COUNT({count: total_session_matches})}
            <PageNavigation bind:currentPage={current_session_page} bind:totalPages={total_session_pages} refresh_function={fetchSessionData}/>
            <div>
                <SessionMatchesDisplay matches={session_matches}/>
            </div>
            <PageNavigation bind:currentPage={current_session_page} bind:totalPages={total_session_pages} refresh_function={fetchSessionData}/>
        {:else}
            {$LL.MODERATOR.ALT_DETECTION.NO_ACCOUNT_MATCHES()}
        {/if}
        
    </Section>
    <Section header={$LL.MODERATOR.ALT_DETECTION.IP_MATCHES()}>
        {#if total_ip_matches}
            {$LL.MODERATOR.ALT_DETECTION.ACCOUNT_MATCH_COUNT({count: total_ip_matches})}
            <PageNavigation bind:currentPage={current_ip_page} bind:totalPages={total_ip_pages} refresh_function={fetchIPData}/>
            <div>
                <IPMatchesDisplay matches={ip_matches}/>
            </div>
            <PageNavigation bind:currentPage={current_ip_page} bind:totalPages={total_ip_pages} refresh_function={fetchIPData}/>
        {:else}
            {$LL.MODERATOR.ALT_DETECTION.NO_ACCOUNT_MATCHES()}
        {/if}
    </Section>
{:else}
    {$LL.COMMON.NO_PERMISSION()}
{/if}