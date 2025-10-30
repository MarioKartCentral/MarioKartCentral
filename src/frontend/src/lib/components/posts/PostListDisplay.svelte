<script lang="ts">
  import type { PostBasic, PostList } from '$lib/types/posts';
  import { onMount } from 'svelte';
  import PostListItem from '$lib/components/posts/PostListItem.svelte';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  import LL from '$i18n/i18n-svelte';

  export let series_id: number | null = null;
  export let tournament_id: number | null = null;

  let posts: PostBasic[] = [];

  let currentPage = 1;
  let totalPages = 0;
  let postCount = 0;

  async function fetchData() {
    let url = '';
    if (tournament_id) {
      url = `/api/tournaments/${tournament_id}/posts?page=${currentPage}`;
    } else if (series_id) {
      url = `/api/tournaments/series/${series_id}/posts?page=${currentPage}`;
    } else {
      url = `/api/posts?page=${currentPage}`;
    }
    const res = await fetch(url);
    if (res.status === 200) {
      const body: PostList = await res.json();
      posts = body.posts;
      postCount = body.count;
      totalPages = body.page_count;
    }
  }

  onMount(fetchData);
</script>

<div class="count">
  {$LL.POSTS.POST_COUNT({ count: postCount })}
</div>
<PageNavigation {currentPage} {totalPages} refresh_function={fetchData} />
{#each posts as post (post.id)}
  <PostListItem {post} {series_id} {tournament_id} />
{/each}
<PageNavigation {currentPage} {totalPages} refresh_function={fetchData} />
