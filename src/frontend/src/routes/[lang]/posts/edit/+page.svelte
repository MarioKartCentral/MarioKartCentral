<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { page } from '$app/stores';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import CreateEditPost from '$lib/components/posts/CreateEditPost.svelte';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, permissions } from '$lib/util/permissions';

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

<Section header={$LL.POSTS.BACK_TO_POST()}>
  <div slot="header_content">
    <Button href="/{$page.params.lang}/posts/view?id={post_id}">{$LL.POSTS.BACK_TO_POST()}</Button>
  </div>
</Section>

{#if user_info.is_checked && post_id}
  {#if check_permission(user_info, permissions.manage_posts)}
    <CreateEditPost id={post_id} />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
