<script lang="ts">
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import LL from "$i18n/i18n-svelte";
    import { onMount } from "svelte";
    import type { APIToken } from "$lib/types/api-tokens";
    import Section from "$lib/components/common/Section.svelte";
    import ApiTokenDisplay from "$lib/components/user/APITokenDisplay.svelte";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let tokens: APIToken[] = [];

    onMount(async() => {
        const endpoint = "/api/user/api_tokens";
        const res = await fetch(endpoint);
        if(res.status === 200) {
            const body: APIToken[] = await res.json();
            tokens = body;
        }
    });
</script>

{#if user_info.is_checked}
    {#if user_info.id === null}
        {$LL.COMMON.LOGIN_REQUIRED()}
    {:else}
        <Section header={$LL.API_TOKENS.API_TOKENS()}>
            {#if tokens.length}
                {#each tokens as token}
                    <ApiTokenDisplay {token}/>
                {/each}
            {/if}
        </Section>
    {/if}
{/if}