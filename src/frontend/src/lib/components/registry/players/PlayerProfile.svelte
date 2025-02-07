<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { UserInfo } from '$lib/types/user-info';
  import Section from '$lib/components/common/Section.svelte';
  import logo from '$lib/assets/logo.png';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import { Avatar } from 'flowbite-svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import DiscordDisplay from '$lib/components/common/discord/DiscordDisplay.svelte';
  import { fc_type_order } from '$lib/util/util';
  import { locale } from '$i18n/i18n-svelte';
  import FCTypeBadge from '$lib/components/badges/FCTypeBadge.svelte';
  import RoleBadge from '$lib/components/badges/RoleBadge.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export let player: PlayerInfo;

  let avatar_url = logo;
  if (player.user_settings && player.user_settings.avatar) {
    avatar_url = player.user_settings.avatar;
  }

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
  };
</script>

<Section header={$LL.PLAYERS.PROFILE.PLAYER_PROFILE()}>
  <div slot="header_content">
    {#if user_info.player_id == player.id}
      <Button href="/{$page.params.lang}/registry/invites">{$LL.PLAYERS.PROFILE.INVITES()}</Button>
      <Button href="/{$page.params.lang}/registry/players/edit-profile"
        >{$LL.PLAYERS.PROFILE.EDIT_PROFILE()}</Button
      >
    {/if}
  </div>
  <div class="wrapper">
    <div class="avatar">
      <Avatar size="xl" src={avatar_url} border alt={player.name}/>
    </div>

    <div class="user_details">
      <div class="name">
        {#if player.country_code}
          <Flag country_code={player.country_code} />
        {/if}
        {player.name}
      </div>
      
      {#if player.friend_codes.length > 0}
        <div class="item">
          <b>{$LL.FRIEND_CODES.FRIEND_CODES()}:</b>
          {#each player.friend_codes.filter((f) => f.is_active).toSorted((a, b) => fc_type_order[a.type] - fc_type_order[b.type]) as fc}
            <div>
              <FCTypeBadge type={fc.type}/>
              {fc.fc}
            </div>
          {/each}
        </div>
      {/if}
      {#if player.rosters.length > 0}
        <div class="item">
          <b>{$LL.PLAYERS.PROFILE.TEAMS()}</b>
          {#each player.rosters as r}
            <div>
              <GameBadge game={r.game}/>
              <ModeBadge mode={r.mode}/>
              <a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">
                {r.roster_name}
              </a>
            </div>
          {/each}
        </div>
      {/if}
      <div class="item">
        {$LL.PLAYERS.PROFILE.REGISTRATION_DATE()} {new Date(player.join_date * 1000).toLocaleString($locale, options)}
      </div>
    </div>
    {#if player.roles.length}
      <div class="item">
        {#each player.roles as role}
          <div>
            <RoleBadge {role}/>
          </div>
        {/each}
      </div>
    {/if}
    <div class="item">
      <DiscordDisplay discord={player.discord}/>
    </div>
    <div class="about_me">
      {#if player.user_settings && player.user_settings.about_me}
        {player.user_settings.about_me}
      {/if}
    </div>
  </div>
</Section>

<style>
  div.wrapper {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    column-gap: 20px;
    margin: 10px 0;
    grid-template-columns: 1fr 2fr 2fr;
  }
  div.user_details {
    display: flex;
    flex-direction: column;
    justify-content: center;
    grid-column-start: 2;
    @media(min-width:800px) {
      justify-content: left;
    }
    
  }
  div.name {
    font-size: 1.5em;
  }
  div.about_me {
    display: flex;
    grid-column-start: 3;
    align-self: flex-start;
    justify-content: center;
    max-width: 400px;
    word-break: break-word;
    @media(min-width: 800px) {
      margin-left: auto;
      margin-right: auto;
    }
    
  }
  div.avatar {
    min-width: 150px;
    margin-bottom: 20px;
    margin-left: 20px;
  }
  div.item {
    margin-top: 10px;
    margin-bottom: 10px;
  }
</style>
