<script lang="ts">
  import PostDisplay from '$lib/components/posts/PostDisplay.svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

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
  {#if post_id}
    <Breadcrumb>
      <BreadcrumbItem home href="/" />
      <BreadcrumbItem href="/{$page.params.lang}/tournaments">{$LL.NAVBAR.TOURNAMENTS()}</BreadcrumbItem>
      <BreadcrumbItem
        href="/{$page.params.lang}/tournaments/details?id={tournament_id}"
        returnText={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>{tournament_id}</BreadcrumbItem
      >
      <BreadcrumbItem current>{$LL.POSTS.TOURNAMENT_ANNOUNCEMENTS()}</BreadcrumbItem>
    </Breadcrumb>
    <PostDisplay id={post_id} {tournament_id} />
  {/if}
{/key}
