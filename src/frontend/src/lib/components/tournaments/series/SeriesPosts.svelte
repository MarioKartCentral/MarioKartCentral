<script lang="ts">
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import Section from '$lib/components/common/Section.svelte';
  import PostListDisplay from '$lib/components/posts/PostListDisplay.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';

  export let series: TournamentSeries;

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });
</script>

<Section header={$LL.POSTS.SERIES_ANNOUNCEMENTS()}>
  <div slot="header_content">
    {#if check_series_permission(user_info, series_permissions.manage_series_posts, series.id)}
      <Button href="/{$page.params.lang}/tournaments/series/posts/create?series_id={series.id}"
        >{$LL.POSTS.CREATE_POST()}</Button
      >
    {/if}
  </div>
  <PostListDisplay series_id={series.id} />
</Section>
