<script lang="ts">
    import { onMount } from "svelte";
    import type { AltFlag, AltFlagList } from "$lib/types/alt-flag";
    import PageNavigation from "$lib/components/common/PageNavigation.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import LL from "$i18n/i18n-svelte";
    import AltFlags from "$lib/components/moderator/AltFlags.svelte";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { check_permission, permissions } from "$lib/util/permissions";

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    let flags: AltFlag[] = [];

    let currentPage = 1;
    let totalFlags = 0;
    let totalPages = 0;

    async function fetchData() {
        const res = await fetch(`/api/moderator/altFlags?page=${currentPage}`);
        if(res.status === 200) {
            const body: AltFlagList = await res.json();
            flags = body.flags;
            totalFlags = body.count;
            totalPages = body.page_count;
        }
    }

    onMount(fetchData);
</script>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.view_alt_flags)}
        <Section header={$LL.MODERATOR.ALT_DETECTION.ALT_FLAGS()}>
            {#if totalFlags}
                <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
                <AltFlags {flags}/>
                <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
            {/if}
        </Section>
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}