<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import TransferList from '$lib/components/registry/teams/TransferList.svelte';
  import ForceTransferPlayer from '$lib/components/registry/teams/ForceTransferPlayer.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { permissions, check_permission } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
</script>

{#if check_permission(user_info, permissions.manage_transfers)}
  <Section header={$LL.MODERATOR.PENDING_TRANSFERS()}>
    <TransferList approval_status="pending"/>
  </Section>
  <Section header={$LL.MODERATOR.MANUALLY_TRANSFER_PLAYER()}>
    <ForceTransferPlayer/>
  </Section>
{:else}
  {$LL.NO_PERMISSION()}
{/if}

