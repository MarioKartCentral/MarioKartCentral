<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CreateEditPost from "$lib/components/posts/CreateEditPost.svelte";
    import { onMount } from "svelte";
    import LL from "$i18n/i18n-svelte";

    let post_id = 0;

    onMount(async () => {
        let param_id = $page.url.searchParams.get('id');
        post_id = Number(param_id);
    });
</script>

<Section header={$LL.POSTS.BACK_TO_POST()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/posts/view?id={post_id}">{$LL.POSTS.BACK_TO_POST()}</Button>
    </div>
</Section>

{#if post_id}
    <CreateEditPost id={post_id}/> 
{/if}
