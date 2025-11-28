<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { UserInfo } from '$lib/types/user-info';
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import { Avatar } from 'flowbite-svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import DiscordDisplay from '$lib/components/common/discord/DiscordDisplay.svelte';
  import { game_order, mode_order, fc_type_order } from '$lib/util/util';
  import { locale } from '$i18n/i18n-svelte';
  import FCTypeBadge from '$lib/components/badges/FCTypeBadge.svelte';
  import RoleBadge from '$lib/components/badges/RoleBadge.svelte';
  import PlayerNameHistory from '$lib/components/registry/players/PlayerNameHistory.svelte';
  import { permissions, check_permission } from '$lib/util/permissions';
  import type { PlayerRoster } from '$lib/types/player-roster';
  import BaggerBadge from '$lib/components/badges/BaggerBadge.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export let player: PlayerInfo;

  let avatar_url = '';
  if (player.user_settings && player.user_settings.avatar) {
    avatar_url = player.user_settings.avatar;
  }

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
  };

  function sort_rosters(rosters: PlayerRoster[]) {
    const mode_sorted = rosters.toSorted((a, b) => mode_order[a.mode] - mode_order[b.mode]);
    return mode_sorted.toSorted((a, b) => game_order[a.game] - game_order[b.game]);
  }
</script>

<Section header={$LL.PLAYERS.PROFILE.PLAYER_PROFILE()}>
  <div slot="header_content">
    {#if user_info.player_id == player.id}
      <Button href="/{$page.params.lang}/registry/invites">{$LL.PLAYERS.PROFILE.INVITES()}</Button>
      <Button href="/{$page.params.lang}/registry/players/edit-profile">{$LL.PLAYERS.PROFILE.EDIT_PROFILE()}</Button>
    {/if}
  </div>
  <div class="wrapper">
    <div class="grid-container">
      <div class="avatar" style="grid-area: a;">
        <Avatar size="xl" src={avatar_url} border alt={player.name} />
      </div>
      <div class="mobile-centered" style="grid-area: b;">
        <div class="name">
          {#if player.country_code}
            <Flag country_code={player.country_code} />
          {/if}
          {player.name}
        </div>
        <PlayerNameHistory {player} />
      </div>
      {#if player.friend_codes.length > 0}
        <div class="mobile-centered" style="grid-area: c;">
          <div class="item">
            <div class="mobile-centered">
              <b>{$LL.FRIEND_CODES.FRIEND_CODES()}:</b>
            </div>
            {#each player.friend_codes
              .filter((f) => f.is_active)
              .toSorted((a, b) => fc_type_order[a.type] - fc_type_order[b.type]) as fc (fc.id)}
              <div>
                <FCTypeBadge type={fc.type} />
                {fc.fc}
              </div>
            {/each}
          </div>
        </div>
      {/if}
      {#if player.rosters.length > 0}
        <div class="mobile-centered" style="grid-area: d;">
          <div class="item">
            <div class="mobile-centered">
              <b>{$LL.PLAYERS.PROFILE.TEAMS()}</b>
            </div>

            {#each sort_rosters(player.rosters) as r (r.roster_id)}
              <div class="teams">
                <div class="badges">
                  <GameBadge game={r.game} />
                  <ModeBadge mode={r.mode} />
                </div>
                <a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">
                  {r.roster_name}
                  {#if r.is_bagger_clause}
                    <BaggerBadge />
                  {/if}
                </a>
              </div>
            {/each}
          </div>
        </div>
      {/if}
      <div class="item mobile-centered" style="grid-area: e;">
        {$LL.PLAYERS.PROFILE.REGISTRATION_DATE()}
        {new Date(player.join_date * 1000).toLocaleString($locale, options)}
      </div>
      {#if player.roles.length}
        <div class="item centered" style="grid-area: f;">
          <div>
            {#each player.roles as role (role.id)}
              <div>
                <RoleBadge {role} />
              </div>
            {/each}
          </div>
        </div>
      {/if}
      {#if !player.user_settings || !player.user_settings.hide_discord || check_permission(user_info, permissions.edit_player)}
        <div class="item centered" style="grid-area: g;">
          <DiscordDisplay discord={player.discord} displayJoinDate />
        </div>
      {/if}
      {#if player.user_settings && player.user_settings.about_me}
        <div class="about_me" style="grid-area: h;">
          {player.user_settings.about_me}
        </div>
      {/if}
    </div>
  </div>
</Section>

<style>
  div.wrapper {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    column-gap: 20px;
    margin: 10px 0;
    grid-template-columns: 1fr 2fr 2fr;
    @media (max-width: 1023px) {
      justify-content: center;
    }
  }
  div.grid-container {
    display: grid;
    column-gap: 20px;
    @media (min-width: 1024px) {
      margin-left: 20px;
      grid-template-areas:
        'a b h'
        'a c h'
        'f d h'
        'g e h'
        'g . h';
    }
    @media (max-width: 1023px) {
      grid-template-areas:
        'a'
        'b'
        'f'
        'g'
        'c'
        'd'
        'e'
        'h';
    }
  }
  div.name {
    font-size: 1.5em;
    width: max-content;
  }
  div.about_me {
    display: flex;
    grid-column-start: 3;
    align-self: flex-start;
    justify-content: center;
    max-width: 400px;
    max-height: 200px;
    overflow: hidden;
    word-break: break-word;
    white-space: pre-line;
    overflow-y: auto;
    @media (min-width: 1024px) {
      margin-left: auto;
      margin-right: auto;
    }
  }
  div.avatar {
    display: flex;
    justify-content: center;
    min-width: 150px;
    margin-bottom: 20px;
  }
  div.item {
    margin-top: 10px;
    margin-bottom: 10px;
  }
  div.centered {
    display: flex;
    justify-content: center;
  }
  div.mobile-centered {
    display: flex;
    @media (max-width: 1023px) {
      justify-content: center;
    }
  }
  div.teams {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  div.badges {
    display: flex;
    flex-wrap: wrap;
    @media (max-width: 1023px) {
      max-width: 110px;
      margin-bottom: 5px;
    }
  }
</style>
