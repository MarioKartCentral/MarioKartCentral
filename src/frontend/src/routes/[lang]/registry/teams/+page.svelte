<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
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

  let teams: Team[] = [];

  onMount(async () => {
    const res = await fetch('/api/registry/teams');
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        teams.push(t);
      }
      teams = teams;
    }
  });
</script>

<Section header={$LL.TEAM_LIST.TEAM_LISTING()}>
  <div slot="header_content">
    {#if user_info.player_id && check_permission(user_info, permissions.create_team, true)}
      <Button href="/{$page.params.lang}/registry/teams/create">{$LL.TEAM_LIST.CREATE_TEAM()}</Button>
    {/if}
  </div>
  {teams.length}
  {$LL.TEAM_LIST.TEAMS()}
  <TeamList {teams} />
</Section>

<style>
</style>
