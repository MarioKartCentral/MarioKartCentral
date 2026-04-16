<script lang="ts">
  import PostDisplay from '$lib/components/posts/PostDisplay.svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

  let post_id = 0;
  let series_id = 0;

  onMount(async () => {
    let s_param_id = $page.url.searchParams.get('series_id');
    series_id = Number(s_param_id);
    let param_id = $page.url.searchParams.get('id');
    post_id = Number(param_id);
  });
</script>

{#key post_id}
  {#if post_id}
    <Breadcrumb>
      <BreadcrumbItem home href="/" />
      <BreadcrumbItem href="/{$page.params.lang}/tournaments/series">{$LL.NAVBAR.TOURNAMENT_SERIES()}</BreadcrumbItem>
      <BreadcrumbItem
        href="/{$page.params.lang}/tournaments/series/details?id={series_id}"
        returnText={$LL.TOURNAMENTS.SERIES.BACK_TO_SERIES()}>{series_id}</BreadcrumbItem
      >
      <BreadcrumbItem current>{$LL.POSTS.SERIES_ANNOUNCEMENTS()}</BreadcrumbItem>
    </Breadcrumb>
    <PostDisplay id={post_id} {series_id} />
  {/if}
{/key}
