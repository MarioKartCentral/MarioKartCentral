<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { UserSettings } from '$lib/types/user-settings';
  import LL from '$i18n/i18n-svelte';
  import LanguageSelect from '$lib/components/common/LanguageSelect.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import FriendCodeForm from '$lib/components/registry/players/FriendCodeForm.svelte';
  import LinkDiscord from '$lib/components/common/discord/LinkDiscord.svelte';

  let user_info: UserInfo;
  let user_settings: UserSettings | null;
  let fc_dialog: Dialog;

  const color_schemes = ['light', 'dark'];
  const timezones = ['utc'];

  user.subscribe((value) => {
    user_info = value;
  });

  $: player = user_info.player ? user_info.player : null;
  $: user_settings = player?.user_settings ? player.user_settings : null;

  async function editProfile(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    const payload = {
      avatar: data.get('avatar_url')?.toString(),
      about_me: data.get('about_me')?.toString(),
      language: data.get('language')?.toString(),
      color_scheme: data.get('theme')?.toString(),
      timezone: data.get('timezone')?.toString(),
    };
    const endpoint = '/api/user/settings/edit';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.status < 300) {
      window.location.reload();
      alert('Edited profile successfully');
    } else {
      alert(`Editing profile failed: ${result['title']}`);
    }
  }
</script>

<svelte:head>
  <title>{$LL.PLAYER_PROFILE.EDIT_PROFILE()} | Mario Kart Central</title>
</svelte:head>

{#if player}
  <Section header={$LL.PLAYER_PROFILE.PLAYER_PROFILE()}>
    <div slot="header_content">
      <Button href="/{$page.params.lang}/registry/players/profile?id={player.id}">Back to Profile</Button>
    </div>
  </Section>
{/if}


<Section header={$LL.PLAYER_PROFILE.FRIEND_CODES()}>
{#if player}
    {#each player.friend_codes as fc}
      <div>
        <GameBadge game={fc.game}/>
        {fc.fc}
      </div>
    {/each}
  <div class="button">
    <Button on:click={fc_dialog.open}>{$LL.PLAYER_PROFILE.ADD_FRIEND_CODE()}</Button>
  </div>
{/if}
</Section>

<Section header="Discord">
  <LinkDiscord/>
</Section>

<Section header="Edit Profile">
{#if user_settings}
<form method="post" on:submit|preventDefault={editProfile}>
  <div>
    <label for="avatar_url">{$LL.PLAYER_PROFILE.AVATAR_URL()}</label>
    <br />
    <input name="avatar_url" type="text" value={user_settings?.avatar ? user_settings.avatar : ''} />
  </div>
  <div>
    <label for="about_me">{$LL.PLAYER_PROFILE.ABOUT_ME()}</label>
    <br />
    <textarea name="about_me">{user_settings?.about_me ? user_settings.about_me : ''}</textarea>
  </div>
  <div>
    <label for="language">{$LL.PLAYER_PROFILE.LANGUAGE()}</label>
    <br />
    <LanguageSelect bind:language={user_settings.language}/>
  </div>
  <div>
    <label for="theme">{$LL.PLAYER_PROFILE.THEME()}</label>
    <br />
    <select name="theme">
      {#each color_schemes as theme}
        <option value={theme}>{theme}</option>
      {/each}
    </select>
  </div>
  <div>
    <label for="timezone">{$LL.PLAYER_PROFILE.TIMEZONE()}</label>
    <br />
    <select name="timezone">
      {#each timezones as tz}
        <option value={tz}>{tz}</option>
      {/each}
    </select>
  </div>
  <div class="button">
    <Button type="submit">{$LL.PLAYER_PROFILE.SAVE()}</Button>
  </div>
  
</form>
{/if}
</Section>

<Dialog bind:this={fc_dialog} header={$LL.PLAYER_PROFILE.ADD_FRIEND_CODE()}>
  <FriendCodeForm {player}/>
</Dialog>
  

<style>
  div.button {
    margin-top: 20px;
  }
</style>
