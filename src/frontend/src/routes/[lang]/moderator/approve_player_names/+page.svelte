<script lang="ts">
  import { check_permission, permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import Section from '$lib/components/common/Section.svelte';
  import LL from '$i18n/i18n-svelte';
  import PlayerNameChangeList from '$lib/components/moderator/PlayerNameChangeList.svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
</script>

{#if check_permission(user_info, permissions.edit_player)}
  <Section header={$LL.MODERATOR.PENDING_NAME_REQUESTS()}>
    <PlayerNameChangeList approval_status="pending" />
  </Section>
  <Section header={$LL.MODERATOR.APPROVED_NAME_REQUESTS()}>
    <PlayerNameChangeList approval_status="approved" />
  </Section>
  <Section header={$LL.MODERATOR.DENIED_NAME_REQUESTS()}>
    <PlayerNameChangeList approval_status="denied" />
  </Section>
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}
