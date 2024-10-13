<script lang="ts">
    import { page } from '$app/stores';
    import LL from '$i18n/i18n-svelte';
    import LanguageSelect from '$lib/components/common/LanguageSelect.svelte';
    import Section from '$lib/components/common/Section.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import LinkDiscord from '$lib/components/common/discord/LinkDiscord.svelte';
    import { check_permission, permissions } from '$lib/util/permissions';
    import type { PlayerInfo } from '$lib/types/player-info';
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import EditFriendCodes from './EditFriendCodes.svelte';
    import EditPlayerDetails from './EditPlayerDetails.svelte';

    export let player: PlayerInfo;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    async function editProfile(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            avatar: data.get('avatar_url')?.toString(),
            about_me: data.get('about_me')?.toString(),
            language: data.get('language')?.toString(),
            color_scheme: 'light',
            timezone: 'utc'
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

    async function forceEditProfile(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            player_id: player.id,
            avatar: data.get('avatar_url')?.toString(),
            about_me: data.get('about_me')?.toString(),
            language: data.get('language')?.toString(),
            color_scheme: 'light',
            timezone: 'utc'
        };
        const endpoint = '/api/user/settings/forceEdit';
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

<Section header={$LL.PLAYER_PROFILE.PLAYER_PROFILE()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/registry/players/profile?id={player.id}">Back to Profile</Button>
    </div>
</Section>

{#if check_permission(user_info, permissions.edit_profile, true)}
    <Section header="Player Details">
        <EditPlayerDetails {player} is_privileged={check_permission(user_info, permissions.edit_player)}/>
    </Section>
    <Section header={$LL.PLAYER_PROFILE.FRIEND_CODES()}>
        <EditFriendCodes {player} is_privileged={check_permission(user_info, permissions.edit_player)}/>
    </Section>
{/if}

{#if player.id === user_info.player?.id}
    <Section header="Discord">
        <LinkDiscord/>
    </Section>
{/if}

<Section header="Edit Profile">
  {#if player.user_settings}
    <form method="post" on:submit|preventDefault={user_info.player?.id === player.id ? editProfile : forceEditProfile}>
      <div>
        <label for="avatar_url">{$LL.PLAYER_PROFILE.AVATAR_URL()}</label>
        <br />
        <input name="avatar_url" type="text" value={player.user_settings?.avatar ? player.user_settings.avatar : ''} />
      </div>
      <div>
        <label for="about_me">{$LL.PLAYER_PROFILE.ABOUT_ME()}</label>
        <br />
        <textarea name="about_me">{player.user_settings?.about_me ? player.user_settings.about_me : ''}</textarea>
      </div>
      <div>
        <label for="language">{$LL.PLAYER_PROFILE.LANGUAGE()}</label>
        <br />
        <LanguageSelect bind:language={player.user_settings.language}/>
      </div>
      <div class="button">
        <Button type="submit" disabled={!check_permission(user_info, permissions.edit_profile, true)}>{$LL.PLAYER_PROFILE.SAVE()}</Button>
      </div>
    </form>
  {/if}
</Section>

<style>
  div.button {
    margin-top: 20px;
  }
</style>
