<script lang="ts">
    import { onMount } from "svelte";
    import { check_permission, permissions } from "$lib/util/permissions";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import LL from "$i18n/i18n-svelte";
    import type { SessionMatch, SessionMatchList } from "$lib/types/account-matches";
    import PageNavigation from "$lib/components/common/PageNavigation.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import SessionMatchesDisplay from "$lib/components/moderator/SessionMatchesDisplay.svelte";

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    let currentPage = 1;

    let session_matches: SessionMatch[] = [];
    let totalMatches = 0;
    let totalPages = 0;

    async function fetchData() {
        const res = await fetch(`/api/moderator/session_matches?page=${currentPage}`);
        if(res.status === 200) {
            const body: SessionMatchList = await res.json();
            session_matches = body.session_matches;
            totalMatches = body.match_count;
            totalPages = body.page_count;
        }
    }

    onMount(fetchData);
</script>

{#if check_permission(user_info, permissions.view_account_matches)}
    <Section header="Cookie Matches">
        {totalMatches} account matches
        <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
        <div>
            <SessionMatchesDisplay matches={session_matches}/>
        </div>
        <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
    </Section>
{:else}
    {$LL.COMMON.NO_PERMISSION()}
{/if}