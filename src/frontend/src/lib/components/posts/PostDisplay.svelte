<script lang="ts">
    import type { Post } from "$lib/types/posts";
    import Section from "../common/Section.svelte";
    import { onMount } from "svelte";
    import PlayerName from "../common/PlayerName.svelte";
    import { locale } from "$i18n/i18n-svelte";
    import MarkdownBox from "../common/MarkdownBox.svelte";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { check_permission, check_series_permission, check_tournament_permission, permissions, series_permissions, tournament_permissions } from "$lib/util/permissions";
    import Button from "../common/buttons/Button.svelte";
    import { page } from "$app/stores";
    import type { Tournament } from "$lib/types/tournament";
    import LL from "$i18n/i18n-svelte";

    export let id: number;
    export let series_id: number | null = null;
    export let tournament_id: number | null = null;
    
    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let post: Post | null = null;

    onMount(async() => {
        let path = tournament_id ? `tournaments/${tournament_id}/` : series_id ? `tournaments/series/${series_id}/`: ``;
        let url = `/api/${path}posts/${id}`;
        const res = await fetch(url);
        if(res.status === 200) {
            const body: Post = await res.json();
            post = body;
        }

        // get the series ID from tournament ID if it's passed in
        if(tournament_id) {
            let tournament_url = `/api/tournaments/${tournament_id}`;
            const res2 = await fetch(tournament_url);
            if(res2.status === 200) {
                const body: Tournament = await res.json();
                series_id = body.series_id;
            }
        }
    });

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'medium',
        timeStyle: 'short',
    };
    
</script>

<svelte:head>
  <title>{post ? post.title : "Posts"} | MKCentral</title>
</svelte:head>

{#if post}
    <Section header={post.title}>
        <div slot="header_content">
            {#if tournament_id && check_tournament_permission(user_info, tournament_permissions.manage_tournament_posts, tournament_id, series_id)}
                <Button href="/{$page.params.lang}/tournaments/posts/edit?tournament_id={tournament_id}&id={id}">{$LL.COMMON.EDIT()}</Button>
            {:else if series_id && check_series_permission(user_info, series_permissions.manage_series_posts, series_id)}
                <Button href="/{$page.params.lang}/tournaments/series/posts/edit?series_id={series_id}&id={id}">{$LL.COMMON.EDIT()}</Button>
            {:else if check_permission(user_info, permissions.manage_posts)}
                <Button href="/{$page.params.lang}/posts/edit?id={id}">{$LL.COMMON.EDIT()}</Button>
            {/if}
        </div>
        <div class="flex">
            {#if post.created_by}
                <PlayerName player={post.created_by}/>
            {/if}
            <div class="date">
                {new Date(post.creation_date * 1000).toLocaleString($locale, options)}
            </div>
        </div>
        <div class="content">
            <MarkdownBox content={post.content}/>
        </div>
    </Section>
{/if}

<style>
    .flex {
        display: flex;
        gap: 10px;
        align-items: center;
    }
</style>