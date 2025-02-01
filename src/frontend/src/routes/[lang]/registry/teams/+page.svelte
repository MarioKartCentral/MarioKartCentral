<script lang="ts">
  import { page } from '$app/stores';
  import Section from '$lib/components/common/Section.svelte';
  import TeamList from '$lib/components/registry/teams/TeamList.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import LL from '$i18n/i18n-svelte';
  import { check_permission, permissions } from '$lib/util/permissions';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });
</script>

<Section header={$LL.TEAMS.LIST.TEAM_LISTING()}>
  <div slot="header_content">
    {#if user_info.player_id && check_permission(user_info, permissions.create_team, true)}
      <Button href="/{$page.params.lang}/registry/teams/create">{$LL.TEAMS.LIST.CREATE_TEAM()}</Button>
    {/if}
  </div>
  <TeamList />
</Section>