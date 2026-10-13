<script lang="ts">
  import PostDisplay from '$lib/components/posts/PostDisplay.svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

  let post_id = 0;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    post_id = Number(param_id);
  });
</script>

{#if post_id}
  <Breadcrumb>
    <BreadcrumbItem home href="/" />
    <BreadcrumbItem href="/{$page.params.lang}/posts" returnText={$LL.POSTS.BACK_TO_ANNOUNCEMENTS()}
      >{$LL.POSTS.ANNOUNCEMENTS()}</BreadcrumbItem
    >
    <BreadcrumbItem current>{post_id}</BreadcrumbItem>
  </Breadcrumb>
  <PostDisplay id={post_id} />
{/if}
