<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import type { Fingerprint } from "$lib/types/fingerprint";
    import Section from "$lib/components/common/Section.svelte";
    import LL from "$i18n/i18n-svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { check_permission, permissions } from "$lib/util/permissions";
    import { goto } from "$app/navigation";

    let hash: string = '';
    let fingerprint: Fingerprint | null = null;

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    async function fetchData() {
        const res = await fetch(`/api/moderator/fingerprints/${hash}`);
        if(res.status === 200) {
            const body: Fingerprint = await res.json();
            fingerprint = body;
        }
        else {
            fingerprint = null;
        }
        $page.url.searchParams.set('hash', hash);
        goto(`?${$page.url.searchParams.toString()}`);
    }

    onMount(async() => {
        let param_hash = $page.url.searchParams.get('hash');
        if(param_hash) {
            hash = param_hash;
        }
        await fetchData();
    });

    function formatData(data: object) {
        return JSON.stringify(data, undefined, 4);
    }
</script>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.view_fingerprints)}
        <Section header={$LL.MODERATOR.ALT_DETECTION.SEARCH_FOR_FINGERPRINTS()}>
            <div>
                <input type="search" placeholder="Search by hash..." bind:value={hash}/>
                <Button on:click={fetchData}>{$LL.COMMON.SEARCH()}</Button>
            </div>
        </Section>
        {#if fingerprint}
            <Section header={$LL.MODERATOR.ALT_DETECTION.FINGERPRINT_HASH({"hash": fingerprint.hash})}>
                <div class="whitespace-pre-line">
                    {formatData(fingerprint.data)}
                </div>
            </Section>
        {/if}
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}

