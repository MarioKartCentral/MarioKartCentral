<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CreateEditPost from "$lib/components/posts/CreateEditPost.svelte";
    import LL from "$i18n/i18n-svelte";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { check_permission, permissions } from "$lib/util/permissions";

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });
</script>

<Section header={$LL.POSTS.BACK_TO_ANNOUNCEMENTS()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/posts">{$LL.COMMON.BACK()}</Button>
    </div>
</Section>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.manage_posts)}
        <CreateEditPost/>
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}
