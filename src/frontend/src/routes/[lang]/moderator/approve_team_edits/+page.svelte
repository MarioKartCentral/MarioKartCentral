<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { check_permission, permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import LL from '$i18n/i18n-svelte';
  import TeamNameChangeList from '$lib/components/moderator/TeamNameChangeList.svelte';
  import RosterNameChangeList from '$lib/components/moderator/RosterNameChangeList.svelte';


  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
</script>

{#if check_permission(user_info, permissions.manage_teams)}
  <Section header="{$LL.MODERATOR.PENDING_TEAM_EDIT_REQUESTS()}">
    <TeamNameChangeList approval_status="pending"/>
  </Section>

  <Section header={$LL.MODERATOR.PENDING_ROSTER_EDIT_REQUESTS()}>
      <RosterNameChangeList approval_status="pending"/>
  </Section>
  <Section header="Approved Team Edit Requests">
    <TeamNameChangeList approval_status="approved"/>
  </Section>
  <Section header="Denied Team Edit Requests">
    <TeamNameChangeList approval_status="denied"/>
  </Section>
  <Section header="Approved Roster Edit Requests">
    <RosterNameChangeList approval_status="approved"/>
  </Section>
  <Section header="Denied Roster Edit Requests">
    <RosterNameChangeList approval_status="denied"/>
  </Section>
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}