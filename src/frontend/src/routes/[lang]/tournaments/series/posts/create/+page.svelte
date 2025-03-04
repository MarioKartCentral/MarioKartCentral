<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CreateEditPost from "$lib/components/posts/CreateEditPost.svelte";
    import { onMount } from "svelte";
    import LL from "$i18n/i18n-svelte";

    let series_id = 0;

    onMount(async () => {
        let s_param_id = $page.url.searchParams.get('series_id');
        series_id = Number(s_param_id);
    });
</script>

<Section header={$LL.TOURNAMENTS.SERIES.BACK_TO_SERIES()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/tournaments/series/details?id={series_id}">{$LL.COMMON.BACK()}</Button>
    </div>
</Section>

<CreateEditPost {series_id}/> 