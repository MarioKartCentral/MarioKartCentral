<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CreateEditPost from "$lib/components/posts/CreateEditPost.svelte";
    import LL from "$i18n/i18n-svelte";
</script>

<Section header={$LL.POSTS.BACK_TO_ANNOUNCEMENTS()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/posts">{$LL.COMMON.BACK()}</Button>
    </div>
</Section>

<CreateEditPost/> 