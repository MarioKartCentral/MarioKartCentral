<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditPost from '$lib/components/posts/CreateEditPost.svelte';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

  let tournament_id = 0;

  onMount(async () => {
    let t_param_id = $page.url.searchParams.get('tournament_id');
    tournament_id = Number(t_param_id);
  });
</script>

{#if tournament_id}
  <Breadcrumb>
    <BreadcrumbItem home href="/" />
    <BreadcrumbItem href="/{$page.params.lang}/tournaments">{$LL.NAVBAR.TOURNAMENTS()}</BreadcrumbItem>
    <BreadcrumbItem
      href="/{$page.params.lang}/tournaments/details?id={tournament_id}"
      returnText={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>{tournament_id}</BreadcrumbItem
    >
    <BreadcrumbItem current>{$LL.POSTS.CREATE_POST()}</BreadcrumbItem>
  </Breadcrumb>

  <CreateEditPost tournamentId={tournament_id} />
{/if}
