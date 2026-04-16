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

  let post_id = 0;
  let series_id = 0;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    post_id = Number(param_id);
    let s_param_id = $page.url.searchParams.get('series_id');
    series_id = Number(s_param_id);
  });
</script>

{#if post_id}
  <Breadcrumb>
    <BreadcrumbItem home href="/" />
    <BreadcrumbItem href="/{$page.params.lang}/tournaments/series">{$LL.NAVBAR.TOURNAMENT_SERIES()}</BreadcrumbItem>
    <BreadcrumbItem href="/{$page.params.lang}/tournaments/series/details?id={series_id}">{series_id}</BreadcrumbItem>
    <BreadcrumbItem>{$LL.POSTS.SERIES_ANNOUNCEMENTS()}</BreadcrumbItem>
    <BreadcrumbItem
      href="/{$page.params.lang}/tournaments/series/posts/view?series_id={series_id}&id={post_id}"
      returnText={$LL.POSTS.BACK_TO_POST()}>{post_id}</BreadcrumbItem
    >
    <BreadcrumbItem current>{$LL.POSTS.EDIT_POST()}</BreadcrumbItem>
  </Breadcrumb>
{/if}
{#if user_info.is_checked && series_id}
  {#if check_series_permission(user_info, series_permissions.manage_series_posts, series_id)}
    {#key post_id}
      <CreateEditPost postId={post_id} seriesId={series_id} />
    {/key}
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
