<script lang="ts">
  import HomeSection from './HomeSection.svelte';
  import type { PostList, PostBasic } from '$lib/types/posts';
  import { onMount } from 'svelte';
  import PostListItem from '../posts/PostListItem.svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';

  export let style: string;

  let posts: PostBasic[] = [];

  async function fetchLatestAnnouncements() {
    let url = '/api/posts';
    const res = await fetch(url);
    if (res.status === 200) {
      const body: PostList = await res.json();
      posts = body.posts;
    }
  }

  onMount(fetchLatestAnnouncements);
</script>

<HomeSection
  header={$LL.POSTS.ANNOUNCEMENTS()}
  {style}
  linkText={$LL.HOMEPAGE.VIEW_ALL_ANNOUNCEMENTS()}
  link="/{$page.params.lang}/posts"
>
  {#each posts.slice(0, 5) as post}
    <PostListItem {post} />
  {/each}
</HomeSection>
