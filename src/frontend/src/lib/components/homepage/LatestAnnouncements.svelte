<script lang="ts">
    import HomeSection from "./HomeSection.svelte";
    import type { PostList, PostBasic } from "$lib/types/posts";
    import { onMount } from "svelte";
    import PostListItem from "../common/PostListItem.svelte";

    export let style: string;

    let posts: PostBasic[] = [];

    async function fetchLatestAnnouncements() {
        let url = '/api/posts';
        const res = await fetch(url);
        if(res.status === 200) {
            const body: PostList = await res.json();
            posts = body.posts;
        }
    }

    onMount(fetchLatestAnnouncements);
</script>

<HomeSection header="Announcements" {style}>
    {#each posts as post}
        <PostListItem {post}/>
    {/each}
</HomeSection>