<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CreateEditPost from "$lib/components/posts/CreateEditPost.svelte";
    import { onMount } from "svelte";
    import LL from "$i18n/i18n-svelte";

    let tournament_id = 0;

    onMount(async () => {
        let t_param_id = $page.url.searchParams.get('tournament_id');
        tournament_id = Number(t_param_id);
    });
</script>

<Section header={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/tournaments/details?id={tournament_id}">{$LL.COMMON.BACK()}</Button>
    </div>
</Section>

<CreateEditPost {tournament_id}/> 