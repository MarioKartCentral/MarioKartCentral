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

<Section header={$LL.MODERATOR.SHADOW_PLAYERS()}>
    <div slot="header_content">
        {#if check_permission(user_info, permissions.manage_shadow_players)}
            <Button on:click={dialog.open}>{$LL.MODERATOR.CREATE_SHADOW_PLAYER()}</Button>
        {/if}
    </div>
    
    <PlayerList is_shadow={true}/>
</Section>

<CreateShadowPlayerDialog bind:this={dialog}/>