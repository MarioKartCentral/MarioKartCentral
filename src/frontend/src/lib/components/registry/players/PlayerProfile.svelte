<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { UserInfo } from '$lib/types/user-info';
  import Section from '$lib/components/common/Section.svelte';
  import logo from '$lib/assets/logo.png';
  import LinkButton from '$lib/components/common/LinkButton.svelte';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export let player: PlayerInfo;

  let avatar_url = logo;
  if (player.user_settings && player.user_settings.avatar) {
    avatar_url = player.user_settings.avatar;
  }
</script>

<Section header="Player Profile">
  <div slot="header_content">
    {#if user_info.player_id == player.id}
      <LinkButton href="/{$page.params.lang}/registry/invites">Invites</LinkButton>
      <LinkButton href="/{$page.params.lang}/registry/players/edit-profile">Edit Profile</LinkButton>
    {/if}
  </div>
  <div class="wrapper">
    <div>
      <img class="avatar" src={avatar_url} alt={player.name} />
    </div>

    <div class="user_details">
      <div class="name">
        {player.name}
      </div>
      <div>
        <b>Country:</b>
        <img src={"/src/lib/assets/flags/" + player.country_code?.toUpperCase() +".png"} alt={player.country_code}/>
        {$LL.COUNTRY[player.country_code]()}
      </div>
      {#if player.friend_codes.length > 0}
        <div>
          <b>Friend Codes:</b>
          {#each player.friend_codes as fc}
            <div class="fc">
              {fc.fc} ({fc.game.toUpperCase()})
            </div>
          {/each}
        </div>
      {/if}
      {#if player.rosters.length > 0}
        <div>
          <b>Teams:</b>
          {#each player.rosters as r}
            <div class="roster">
              <a href="/{$page.params.lang}/registry/teams/profile?id={r.team_id}">
                {r.roster_name} ({r.game}
                {r.mode})
              </a>
            </div>
          {/each}
        </div>
      {/if}
    </div>
    {#if player.user_settings && player.user_settings.about_me}
      <div class="about_me">
        {player.user_settings.about_me}
      </div>
    {/if}
  </div>
</Section>

<style>
  /* div.container {
    margin: 10px 0;
  }
  div.header {
    display: grid;
    grid-template-columns: 3fr 1fr;
    background-color: green;
  }
  div.header_element {
    margin: 5px;
  } */
  div.wrapper {
    display: inline-grid;
    column-gap: 20px;
    margin: 10px 0;
    grid-template-columns: 1fr 2fr 2fr;
  }
  div.user_details {
    grid-column-start: 2;
  }
  div.name {
    font-size: 1.5em;
  }
  div.about_me {
    grid-column-start: 3;
  }
  div.fc {
    text-indent: 2em;
  }
  div.roster {
    text-indent: 2em;
  }
  img.avatar {
    width: 150px;
    height: 150px;
    margin: 10px;
    border: 5px white solid;
    border-radius: 50%;
    object-fit: cover;
  }
</style>
