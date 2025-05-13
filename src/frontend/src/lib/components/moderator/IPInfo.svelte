<script lang="ts">
    import type { IPAddress, IPAddressWithUserCount } from "$lib/types/ip-addresses";
    import { page } from "$app/stores";
    import LL from "$i18n/i18n-svelte";
    import Flag from "../common/Flag.svelte";

    export let ip: IPAddress | IPAddressWithUserCount;

    function hasCount(ip: IPAddress | IPAddressWithUserCount): ip is IPAddressWithUserCount {
        return (ip as IPAddressWithUserCount).user_count !== undefined;
    }
</script>

<a href="/{$page.params.lang}/moderator/ip_history?id={ip.id}">
    <div class="ip-container">
        <div>
            ID: {ip.id}
        </div>
        {#if ip.ip_address}
            <div>
                {ip.ip_address}
            </div>
        {/if}
        <div>
            {$LL.MODERATOR.ALT_DETECTION.VPN()}: {ip.is_vpn ? $LL.COMMON.YES() : $LL.COMMON.NO()}
        </div>
        <div>
            {$LL.MODERATOR.ALT_DETECTION.MOBILE()}: {ip.is_mobile ? $LL.COMMON.YES() : $LL.COMMON.NO()}
        </div>
        {#if ip.country}
            <div>
                <Flag country_code={ip.country.toLowerCase()}/>
            </div>
        {/if}
        {#if ip.region}
            <div>
                {ip.region}
            </div>
        {/if}
        {#if ip.city}
            <div>
                {ip.city}
            </div>
        {/if}
        {#if ip.asn}
            <div>
                ASN: {ip.asn}
            </div>
        {/if}
        {#if hasCount(ip)}
            <div>
                {$LL.MODERATOR.ALT_DETECTION.IP_USER_COUNT({"count": ip.user_count})}
            </div>
        {/if}
    </div>
</a>

<style>
    .ip-container {
        margin-top: 10px;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        background-color: rgba(255, 255, 255, 0.15);
        padding: 0px 10px;
        align-items: center;
        min-height: 45px;
    }
</style>