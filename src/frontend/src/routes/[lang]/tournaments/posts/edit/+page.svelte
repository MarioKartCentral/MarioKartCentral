<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditPost from '$lib/components/posts/CreateEditPost.svelte';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

  let post_id = 0;
  let tournament_id = 0;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    post_id = Number(param_id);
    let t_param_id = $page.url.searchParams.get('tournament_id');
    tournament_id = Number(t_param_id);
  });
</script>

{#if tournament_id && post_id}
  <Breadcrumb>
    <BreadcrumbItem home href="/" />
    <BreadcrumbItem href="/{$page.params.lang}/tournaments">{$LL.NAVBAR.TOURNAMENTS()}</BreadcrumbItem>
    <BreadcrumbItem href="/{$page.params.lang}/tournaments/details?id={tournament_id}">{tournament_id}</BreadcrumbItem>
    <BreadcrumbItem>{$LL.POSTS.TOURNAMENT_ANNOUNCEMENTS()}</BreadcrumbItem>
    <BreadcrumbItem
      href="/{$page.params.lang}/tournaments/posts/view?tournament_id={tournament_id}&id={post_id}"
      returnText={$LL.POSTS.BACK_TO_POST()}>{post_id}</BreadcrumbItem
    >
    <BreadcrumbItem current>{$LL.POSTS.EDIT_POST()}</BreadcrumbItem>
  </Breadcrumb>
{/if}

{#key post_id}
  <CreateEditPost postId={post_id} tournamentId={tournament_id} />
{/key}
