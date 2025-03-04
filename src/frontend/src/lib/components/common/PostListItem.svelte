<script lang="ts">
    import type { PostBasic } from "$lib/types/posts";
    import Flag from "./Flag.svelte";
    import { locale } from "$i18n/i18n-svelte";
    import { page } from "$app/stores";

    export let post: PostBasic;

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'medium',
    };
</script>

<div class="wrapper">
    <div class="title">
        {post.title}
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