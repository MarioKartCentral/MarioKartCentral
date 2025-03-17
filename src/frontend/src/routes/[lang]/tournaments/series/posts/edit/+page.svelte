<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CreateEditPost from "$lib/components/posts/CreateEditPost.svelte";
    import { onMount } from "svelte";
    import LL from "$i18n/i18n-svelte";

    let post_id = 0;
    let series_id = 0;

    onMount(async () => {
        let param_id = $page.url.searchParams.get('id');
        post_id = Number(param_id);
        let s_param_id = $page.url.searchParams.get('series_id');
        series_id = Number(s_param_id);
    });
</script>

<Section header={$LL.POSTS.BACK_TO_POST()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/tournaments/series/posts/view?series_id={series_id}&id={post_id}">{$LL.COMMON.BACK()}</Button>
    </div>
</Section>

{#key post_id}
    <CreateEditPost id={post_id} {series_id}/> 
{/key}
