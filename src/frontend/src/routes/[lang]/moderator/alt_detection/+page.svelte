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

    let type: string | null = null;
    let exclude_fingerprints = true;
    let from: string | null = null;
    let to: string | null = null;

    async function fetchData() {
        let url = `/api/moderator/altFlags?page=${currentPage}`;
        if(type) {
            url += `&type=${type}`;
        }
        if(exclude_fingerprints) {
            url += `&exclude_fingerprints=true`
        }
        if(from) {
            url += `&from_date=${Date.parse(String(from)) / 1000}`
        }
        if(to) {
            url += `&to_date=${Date.parse(String(to)) / 1000}`
        }
        const res = await fetch(url);
        if(res.status === 200) {
            const body: AltFlagList = await res.json();
            flags = body.flags;
            totalFlags = body.count;
            totalPages = body.page_count;
        }
    }

    async function filter() {
        if(type === "fingerprint_match") {
            exclude_fingerprints = false;
        }
        await fetchData();
    }

    onMount(fetchData);
</script>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.view_alt_flags)}
        <Section header={$LL.MODERATOR.ALT_DETECTION.ALT_FLAGS()}>
            {#if totalFlags}
                <div class="flex gap-4 items-center">
                    <select bind:value={type} on:change={filter}>
                        <option value={null}>
                            All Flags
                        </option>
                        <option value="vpn">
                            VPN
                        </option>
                        <option value="ip_match">
                            IP Matches
                        </option>
                        <option value="persistent_cookie_match">
                            Cookie Matches
                        </option>
                        <option value="fingerprint_match">
                            Fingerprint Matches
                        </option>
                    </select>
                    <select bind:value={exclude_fingerprints} on:change={fetchData}>
                        <option value={true}>{$LL.MODERATOR.ALT_DETECTION.EXCLUDE_FINGERPRINTS()}</option>
                        <option value={false}>{$LL.MODERATOR.ALT_DETECTION.INCLUDE_FINGERPRINTS()}</option>
                    </select>
                    <div class="flex gap-4 items-center">
                        {$LL.COMMON.FROM()}
                        <input name="from" type="date" bind:value={from} on:change={filter}/>
                    </div>
                    <div class="flex gap-4 items-center">
                        {$LL.COMMON.TO()}
                        <input name="to" type="date" bind:value={to} on:change={filter}/>
                    </div>
                </div>
                <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
                {#key flags}
                    <AltFlags {flags}/>
                {/key}
                <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
            {/if}
        </Section>
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}