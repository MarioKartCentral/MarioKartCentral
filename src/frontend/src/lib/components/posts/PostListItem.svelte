<script lang="ts">
    import type { PostBasic } from "$lib/types/posts";
    import Flag from "../common/Flag.svelte";
    import { locale } from "$i18n/i18n-svelte";
    import { page } from "$app/stores";
    import HiddenBadge from "../badges/HiddenBadge.svelte";

    export let post: PostBasic;
    export let series_id: number | null = null;
    export let tournament_id: number | null = null;

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'medium',
    };
</script>

<div class="wrapper {post.is_public ? "" : "post-hidden"}">
    <div class="title flex">
        {#if !post.is_public}
            <HiddenBadge/>
        {/if}
        <a href="/{$page.params.lang}/{tournament_id ? `tournaments/` : series_id ? `tournaments/series/` : ''}posts/view?id={post.id}{tournament_id 
            ? `&tournament_id=${tournament_id}` : ''}{series_id ? `&series_id=${series_id}` : ''}">
            {post.title}
        </a>
    </div>
    <div class="flex">
        {#if post.created_by}
            <a href="/{$page.params.lang}/registry/players/profile?id={post.created_by.id}">
                <div class="player">
                    <div class="flex">
                        <Flag country_code={post.created_by.country_code} size="small"/>
                        {post.created_by.name}
                    </div>
                </div>
            </a>
        {/if}
        <div class="date">
            {new Date(post.creation_date * 1000).toLocaleString($locale, options)}
        </div>
    </div>
</div>

<style>
    .wrapper {
        margin-bottom: 10px;
    }
    .post-hidden {
        opacity: 0.5;
    }
    .title {
        font-size: 1.25em;
        font-weight: 400;
    }
    .flex {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .player {
        font-size: 0.75em;
    }
    .date {
        font-size: 0.75em;
    }
</style>