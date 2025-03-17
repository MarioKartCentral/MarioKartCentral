<script lang="ts">
    import PostListDisplay from "$lib/components/posts/PostListDisplay.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import { check_permission, permissions } from "$lib/util/permissions";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { page } from "$app/stores";
    import LL from "$i18n/i18n-svelte";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });
</script>

<Section header={$LL.POSTS.BACK_TO_HOMEPAGE()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/">{$LL.COMMON.BACK()}</Button>
    </div>
</Section>
<Section header={$LL.POSTS.ANNOUNCEMENTS()}>
    <div slot="header_content">
        {#if check_permission(user_info, permissions.manage_posts)}
            <Button href="/{$page.params.lang}/posts/create">{$LL.POSTS.CREATE_POST()}</Button>
        {/if}
    </div>
    <PostListDisplay/>
</Section>
