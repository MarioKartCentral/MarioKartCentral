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
    import RegisterForm from '$lib/components/login/RegisterForm.svelte';

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
            alert($LL.PLAYERS.PROFILE.PROFILE_EDIT_SUCCESS());
        } else {
            alert(`${$LL.PLAYERS.PROFILE.PROFILE_EDIT_FAILED()}: ${result['title']}`);
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
            alert($LL.PLAYERS.PROFILE.PROFILE_EDIT_SUCCESS());
        } else {
            alert(`${$LL.PLAYERS.PROFILE.PROFILE_EDIT_FAILED()}: ${result['title']}`);
        }
    }

    let old_password = "";
    let new_password = "";
    async function changePassword() {
        const payload = {
            old_password: old_password,
            new_password: new_password,
        };
        const endpoint = '/api/user/reset_password';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if(response.status < 300) {
            alert($LL.LOGIN.PASSWORD_RESET_SUCCESS());
            window.location.reload();
        }
        else {
            alert(`${$LL.LOGIN.PASSWORD_RESET_FAILURE()}: ${result['title']}`);
        }
    }
</script>

<Section header={$LL.PLAYERS.PROFILE.PLAYER_PROFILE()}>
    <div slot="header_content">
        <Button href="/{$page.params.lang}/registry/players/profile?id={player.id}">{$LL.PLAYERS.PROFILE.BACK_TO_PROFILE()}</Button>
    </div>
</Section>

{#if check_permission(user_info, permissions.edit_profile, true)}
    <Section header={$LL.PLAYERS.PROFILE.PLAYER_DETAILS()}>
        <EditPlayerDetails {player} is_privileged={check_permission(user_info, permissions.edit_player)}/>
    </Section>
    <Section header={$LL.FRIEND_CODES.FRIEND_CODES()}>
        <EditFriendCodes {player} is_privileged={check_permission(user_info, permissions.edit_player)}/>
    </Section>
{/if}

{#if player.id === user_info.player?.id}
    <Section header={$LL.DISCORD.DISCORD()}>
        <LinkDiscord/>
    </Section>
    <Section header={$LL.LOGIN.CHANGE_PASSWORD()}>
        <RegisterForm is_reset is_change bind:old_password={old_password} bind:password={new_password} on:submit={changePassword}/>
    </Section>
{/if}

<Section header={$LL.PLAYERS.PROFILE.EDIT_PROFILE()}>
  {#if player.user_settings}
    <form method="post" on:submit|preventDefault={user_info.player?.id === player.id ? editProfile : forceEditProfile}>
      <div>
        <label for="about_me">{$LL.PLAYERS.PROFILE.ABOUT_ME()}</label>
        <br />
        <textarea name="about_me" maxlength=200>{player.user_settings?.about_me ? player.user_settings.about_me : ''}</textarea>
      </div>
      <div>
        <label for="language">{$LL.COMMON.LANGUAGE()}</label>
        <br />
        <LanguageSelect bind:language={player.user_settings.language}/>
      </div>
      <div class="button">
        <Button type="submit" disabled={!check_permission(user_info, permissions.edit_profile, true)}>{$LL.COMMON.SAVE()}</Button>
      </div>
    </form>
  {/if}
</Section>

<style>
  div.button {
    margin-top: 20px;
  }
  textarea {
    width: 100%;
    height: 150px;
  }
</style>
