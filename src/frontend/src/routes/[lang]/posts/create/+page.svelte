<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditPost from '$lib/components/posts/CreateEditPost.svelte';
  import LL from '$i18n/i18n-svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, permissions } from '$lib/util/permissions';
  import Breadcrumb from '$lib/components/common/breadcrumb/Breadcrumb.svelte';
  import BreadcrumbItem from '$lib/components/common/breadcrumb/BreadcrumbItem.svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
</script>

{#if user_info.is_checked}
  <Breadcrumb>
    <BreadcrumbItem home href="/" />
    <BreadcrumbItem href="/{$page.params.lang}/posts" returnText={$LL.POSTS.BACK_TO_ANNOUNCEMENTS()}
      >{$LL.POSTS.ANNOUNCEMENTS()}</BreadcrumbItem
    >
    <BreadcrumbItem current>{$LL.POSTS.CREATE_POST()}</BreadcrumbItem>
  </Breadcrumb>
  {#if check_permission(user_info, permissions.manage_posts)}
    <CreateEditPost />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
