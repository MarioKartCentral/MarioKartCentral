<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditPost from '$lib/components/posts/CreateEditPost.svelte';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let series_id = 0;

  onMount(async () => {
    let s_param_id = $page.url.searchParams.get('series_id');
    series_id = Number(s_param_id);
  });
</script>

{#if series_id}
  <Breadcrumb>
    <BreadcrumbItem home href="/" />
    <BreadcrumbItem href="/{$page.params.lang}/tournaments/series">{$LL.NAVBAR.TOURNAMENT_SERIES()}</BreadcrumbItem>
    <BreadcrumbItem
      href="/{$page.params.lang}/tournaments/series/details?id={series_id}"
      returnText={$LL.TOURNAMENTS.SERIES.BACK_TO_SERIES()}>{series_id}</BreadcrumbItem
    >
    <BreadcrumbItem current>{$LL.POSTS.CREATE_POST()}</BreadcrumbItem>
  </Breadcrumb>
{/if}
{#if user_info.is_checked && series_id}
  {#if check_series_permission(user_info, series_permissions.manage_series_posts, series_id)}
    <CreateEditPost seriesId={series_id} />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
