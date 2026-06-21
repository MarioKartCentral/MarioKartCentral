<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditPost from '$lib/components/posts/CreateEditPost.svelte';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, permissions } from '$lib/util/permissions';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

  let post_id = 0;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    post_id = Number(param_id);
  });
</script>

{#if user_info.is_checked && post_id}
  <Breadcrumb>
    <BreadcrumbItem home href="/" />
    <BreadcrumbItem href="/{$page.params.lang}/posts" returnText={$LL.POSTS.BACK_TO_ANNOUNCEMENTS()}
      >{$LL.POSTS.ANNOUNCEMENTS()}</BreadcrumbItem
    >

    <BreadcrumbItem href="/{$page.params.lang}/posts/view?id={post_id}" returnText={$LL.POSTS.BACK_TO_POST()}
      >{post_id}</BreadcrumbItem
    >

    <BreadcrumbItem current>{$LL.POSTS.EDIT_POST()}</BreadcrumbItem>
  </Breadcrumb>
  {#if check_permission(user_info, permissions.manage_posts)}
    <CreateEditPost postId={post_id} />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
