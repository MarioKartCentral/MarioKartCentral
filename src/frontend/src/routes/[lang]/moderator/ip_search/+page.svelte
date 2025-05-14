<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import LL from "$i18n/i18n-svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { permissions, check_permission } from "$lib/util/permissions";
    import type { IPAddressList, IPAddressWithUserCount } from "$lib/types/ip-addresses";
    import PageNavigation from "$lib/components/common/PageNavigation.svelte";
    import IpInfo from "$lib/components/moderator/IPInfo.svelte";

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    let ip_address = '';
    let city = '';
    let asn = '';
    let currentPage = 1;
    let totalPages = 0;
    let count = 0;

    let results: IPAddressWithUserCount[] = [];

    async function fetchData() {
        let url = `/api/moderator/ip_addresses?page=${currentPage}`;
        if(ip_address) {
            url += `&ip_address=${ip_address}`;
        }
        if(city) {
            url += `&city=${city}`;
        }
        if(asn) {
            url += `&asn=${asn}`;
        }
        const res = await fetch(url);
        if(res.status === 200) {
            const body: IPAddressList = await res.json();
            console.log(body);
            results = body.ip_addresses;
            totalPages = body.page_count;
            count = body.count;
        }
    }

</script>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.view_basic_ip_info)}
        <Section header={$LL.MODERATOR.ALT_DETECTION.IP_SEARCH()}>
            <div class="flex gap-3 flex-wrap">
                {#if check_permission(user_info, permissions.view_ip_addresses)}
                    <input bind:value={ip_address} placeholder={$LL.MODERATOR.ALT_DETECTION.IP_ADDRESS()}/>
                {/if}
                <input bind:value={city} placeholder="City"/>
                <input bind:value={asn} placeholder="ASN"/>
                <Button on:click={fetchData}>{$LL.COMMON.SEARCH()}</Button>
            </div>
        </Section>
        {#if results.length}
            <Section header={$LL.MODERATOR.ALT_DETECTION.IP_ADDRESSES()}>
                {$LL.MODERATOR.ALT_DETECTION.IP_ADDRESS_COUNT({"count": count})}
                <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
                {#each results as result}
                    <IpInfo ip={result}/>
                {/each}
                <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
            </Section>
            
        {/if}
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}