<script lang="ts">
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import { permissions, check_permission } from '$lib/util/permissions';
  import { user as userStore } from '$lib/stores/stores';
  import type { MyDiscord } from '$lib/types/my-discord';
  import DiscordUser from './DiscordUser.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';

  export let userId: number;
  let linkedAccount: MyDiscord | null = null;
  const forceEdit = check_permission($userStore, permissions.edit_user) && userId !== $userStore.id;

  onMount(async () => {
    const endpoint = userId === $userStore.id ? '/api/user/my_discord' : `/api/user/${userId}/discord`;
    const response = await fetch(endpoint);
    if (response.ok) {
      linkedAccount = await response.json();
    }
  });

  async function linkDiscord() {
    window.location.assign('/api/user/link_discord');
  }

  async function refreshDiscordData() {
    const endpoint = '/api/user/refresh_discord';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    const result = await response.json();
    if (!response.ok) {
      alert(`${$LL.DISCORD.REFRESH_ERROR()}: ${result['title']}`);
      return;
    }

    linkedAccount = result;
  }

  async function deleteDiscordData() {
    const confirm = window.confirm($LL.DISCORD.DELETE_DATA_CONFIRM());
    if (!confirm) return;
    const endpoint = '/api/user/delete_discord';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await response.json();
    if (!response.ok) {
      alert(`${$LL.DISCORD.DELETE_DATA_ERROR()}: ${result['title']}`);
      return;
    }

    linkedAccount = null;
  }

  async function forceDeleteDiscordData() {
    const confirm = window.confirm($LL.DISCORD.DELETE_DATA_CONFIRM());
    if (!confirm) return;
    const endpoint = `/api/user/${userId}/discord/forceDelete`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      const result = await response.json();
      alert(`${$LL.DISCORD.DELETE_DATA_ERROR()}: ${result['title']}`);
      return;
    }
    linkedAccount = null;
  }

  async function syncDiscordAvatar() {
    if (!linkedAccount) throw Error('No account linked');
    if (forceEdit) throw Error("Cannot sync another player's avatar");
    const endpoint = '/api/user/sync_discord_avatar';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await response.json();
    if (!response.ok) {
      alert(`${$LL.DISCORD.SYNC_AVATAR_ERROR()}: ${result['title']}`);
      return;
    }

    const { avatar } = result;

    if (!$userStore.player?.user_settings) return;
    $userStore.player.user_settings.avatar = avatar as string;
  }
</script>

{#if $userStore.id === null}
  {$LL.DISCORD.SIGN_IN_REGISTER_TO_LINK()}
{:else}
  <div class="flex items-center flex-wrap gap-2">
    <DiscordUser discord={linkedAccount} />
    <div class="flex items-center flex-wrap gap-2">
      <Button
        size="xs"
        extra_classes="min-w-32"
        on:click={linkDiscord}
        disabled={forceEdit || !check_permission($userStore, permissions.link_discord, true)}
      >
        {linkedAccount ? $LL.DISCORD.RELINK_DISCORD() : $LL.DISCORD.LINK_DISCORD()}
      </Button>
      {#if linkedAccount}
        <Button size="xs" extra_classes="min-w-32" on:click={forceEdit ? forceDeleteDiscordData : deleteDiscordData}>
          {$LL.DISCORD.UNLINK_DISCORD()}
        </Button>
        <Button
          size="xs"
          extra_classes="min-w-32"
          on:click={refreshDiscordData}
          disabled={forceEdit || !check_permission($userStore, permissions.link_discord, true)}
        >
          {$LL.DISCORD.REFRESH()}
        </Button>
        <Button size="xs" extra_classes="min-w-32" on:click={syncDiscordAvatar} disabled={forceEdit}>
          {$LL.DISCORD.SYNC_AVATAR()}
        </Button>
      {/if}
    </div>
  </div>
{/if}
