<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import PlayerList from "$lib/components/registry/players/PlayerList.svelte";
    import { permissions, check_permission } from "$lib/util/permissions";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CreateShadowPlayerDialog from "$lib/components/registry/players/CreateShadowPlayerDialog.svelte";
    import LL from "$i18n/i18n-svelte";

    let dialog: CreateShadowPlayerDialog;

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });
</script>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.manage_shadow_players)}
        <Section header={$LL.MODERATOR.SHADOW_PLAYERS()}>
            <div slot="header_content">
                <Button on:click={dialog.open}>{$LL.MODERATOR.CREATE_SHADOW_PLAYER()}</Button>
            </div>
            <PlayerList is_shadow={true}/>
        </Section>
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}


<CreateShadowPlayerDialog bind:this={dialog}/>
