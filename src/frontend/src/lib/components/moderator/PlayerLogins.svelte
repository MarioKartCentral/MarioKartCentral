<script lang="ts">
    import Dialog from "../common/Dialog.svelte";
    import { onMount } from "svelte";
    import LL from "$i18n/i18n-svelte";
    import type { PlayerUserLogins } from "$lib/types/logins";
    import Table from "../common/Table.svelte";
    import { locale } from "$i18n/i18n-svelte";
    import Button from "../common/buttons/Button.svelte";
    import { page } from "$app/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { permissions, check_permission } from "$lib/util/permissions";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    export let player_id: number;

    let login_dialog: Dialog;
    let logins: PlayerUserLogins;

    export function open() {
        login_dialog.open();
    }

    onMount(async() => {
        const res = await fetch(`/api/moderator/player_logins/${player_id}`);
        if(res.status === 200) {
            const body: PlayerUserLogins = await res.json();
            logins = body;
        }
    });

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };

    // list of indexes which we should show flag data
    let show_ips: Set<number> = new Set([]);

    function toggle_ip(i: number) {
        if(show_ips.has(i)) {
            show_ips.delete(i);
        }
        else {
            show_ips.add(i);
        }
        show_ips = show_ips;
    }
</script>

<Dialog bind:this={login_dialog} header={$LL.MODERATOR.ALT_DETECTION.LOGIN_HISTORY()}>
    {#if logins}
        <Table>
            <col class="date"/>
            <col class="fingerprint"/>
            <col class="ip-show"/>
            <col class="previous-cookie mobile-hide"/>
            <col class="logout-date mobile-hide"/>
            <thead>
                <tr>
                    <th>{$LL.COMMON.DATE()}</th>
                    <th>{$LL.MODERATOR.ALT_DETECTION.FINGERPRINT()}</th>
                    <th>{$LL.MODERATOR.ALT_DETECTION.IP_ADDRESS()}</th>
                    <th class="mobile-hide">{$LL.MODERATOR.ALT_DETECTION.PREVIOUS_COOKIE()}</th>
                    <th class="mobile-hide">{$LL.MODERATOR.ALT_DETECTION.LOGOUT_DATE()}</th>
                </tr>
            </thead>
            <tbody>
                {#each logins.logins as login, i}
                    <tr class="row-{i % 2}">
                        <td>{new Date(login.date * 1000).toLocaleString($locale, options)}</td>
                        {#if check_permission(user_info, permissions.view_fingerprints)}
                            <td>
                                <Button href="/{$page.params.lang}/moderator/fingerprints?hash={login.fingerprint}">
                                    {$LL.COMMON.VIEW()}
                                </Button>
                            </td>
                        {:else}
                            <td>
                                {login.fingerprint}
                            </td>
                        {/if}
                        <td>
                            <Button on:click={() => toggle_ip(i)}>
                                {#if show_ips.has(i)}
                                    {$LL.COMMON.HIDE()}
                                {:else}
                                    {$LL.COMMON.SHOW()}
                                {/if}   
                            </Button>
                        </td>
                        <td class="mobile-hide">
                            {#if login.had_persistent_session}
                                {$LL.COMMON.YES()}
                            {:else}
                                {$LL.COMMON.NO()}
                            {/if}
                        </td>
                        <td class="mobile-hide">
                            {#if login.logout_date}
                                {new Date(login.logout_date * 1000).toLocaleString($locale, options)}
                            {:else}
                                -
                            {/if}
                        </td>
                    </tr>
                    {#if show_ips.has(i)}
                        <tr class="row-{i % 2}">
                            <td colspan=10>
                                
                                <Table>
                                    <col class="ip-id mobile-hide"/>
                                    {#if login.ip_address.ip_address}
                                        <col class="ip-address"/>
                                    {/if}
                                    <col class="country mobile-hide"/>
                                    <col class="is-mobile"/>
                                    <col class="is-vpn"/>
                                    <thead>
                                        <tr>
                                            <th class="mobile-hide">ID</th>
                                            {#if login.ip_address.ip_address}
                                                <th>{$LL.MODERATOR.ALT_DETECTION.IP_ADDRESS()}</th>
                                            {/if}
                                            <th class="mobile-hide">{$LL.COMMON.COUNTRY()}</th>
                                            <th>{$LL.MODERATOR.ALT_DETECTION.MOBILE()}</th>
                                            <th>{$LL.MODERATOR.ALT_DETECTION.VPN()}</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td class="mobile-hide">
                                                <a href="/{$page.params.lang}/moderator/ip_history?id={login.ip_address.id}">
                                                    {login.ip_address.id}
                                                </a>
                                            </td>
                                            {#if login.ip_address.ip_address}
                                                <td>
                                                    <a href="/{$page.params.lang}/moderator/ip_history?id={login.ip_address.id}">
                                                        {login.ip_address.ip_address}
                                                    </a>
                                                </td>
                                            {/if}
                                            <td class="mobile-hide">
                                                {login.ip_address.country}
                                            </td>
                                            <td>
                                                {#if login.ip_address.is_mobile}
                                                    {$LL.COMMON.YES()}
                                                {:else}
                                                    {$LL.COMMON.NO()}
                                                {/if}
                                            </td>
                                            <td>
                                                {#if login.ip_address.is_vpn}
                                                    {$LL.COMMON.YES()}
                                                {:else}
                                                    {$LL.COMMON.NO()}
                                                {/if}
                                            </td>
                                        </tr>
                                    </tbody>
                                </Table>
                            </td>
                        </tr>
                    {/if}
                {/each}
            </tbody>
        </Table>
    {/if}
</Dialog>

<style>
    col.date {
        width: 20%;
    }
    col.fingerprint {
        width: 20%;
    }
    col.ip-show {
        width: 25%;
    }
    col.previous-cookie {
        width: 18%;
    }
    col.logout-date {
        width: 22%;
    }
</style>