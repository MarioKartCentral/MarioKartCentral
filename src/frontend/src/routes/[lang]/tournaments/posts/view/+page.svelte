<script lang="ts">
    import PostDisplay from "$lib/components/posts/PostDisplay.svelte";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import Section from "$lib/components/common/Section.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import LL from "$i18n/i18n-svelte";

    let post_id = 0;
    let tournament_id = 0;

    onMount(async () => {
        let t_param_id = $page.url.searchParams.get('tournament_id');
        tournament_id = Number(t_param_id);
        let param_id = $page.url.searchParams.get('id');
        post_id = Number(param_id);
    });
</script>

{#key post_id}
    <Section header={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>
        <div slot="header_content">
            <Button href="/{$page.params.lang}/tournaments/details?id={tournament_id}">{$LL.COMMON.BACK()}</Button>
        </div>
    </Section>
    {#if post_id}
        <PostDisplay id={post_id} {tournament_id}/>
    {/if}
{/key}