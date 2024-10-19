<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import TransferList from '$lib/components/registry/teams/TransferList.svelte';
  import ForceTransferPlayer from '$lib/components/registry/teams/ForceTransferPlayer.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { permissions, check_permission } from '$lib/util/permissions';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
</script>

{#if check_permission(user_info, permissions.manage_transfers)}
  <Section header="Transfers">
    <TransferList approval_status="pending"/>
  </Section>
  <Section header="Manually Transfer Player">
    <ForceTransferPlayer/>
  </Section>
{:else}
  You do not have permission to view this page.
{/if}

