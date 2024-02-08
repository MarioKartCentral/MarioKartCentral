<script lang="ts">
  import type { Team } from '$lib/types/team';
  import logo from '$lib/assets/logo.png';
  import { LL, locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import Tag from '$lib/components/registry/teams/Tag.svelte';

  export let team: Team;

  let avatar_url = logo;
  if (team.logo) {
    avatar_url = team.logo;
  }

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour12: true,
  };
</script>

<div class="wrapper">
  <div>
    <img class="avatar" src={avatar_url} alt={team.name} />
  </div>
  <div class="team_details">
    <div class="tag">
      <Tag {team} />
    </div>
    <div class="name">
      <b>{team.name}</b>
    </div>
    <div>
      <b>{$LL.TEAM_PROFILE.REGISTERED()}</b>
      {new Date(team.creation_date * 1000).toLocaleString($locale, options)}
    </div>
    <div>
      <b>{$LL.TEAM_PROFILE.MAIN_LANGUAGE()}</b>
      {team.language}
    </div>
    <div>
      <b>{$LL.TEAM_PROFILE.MANAGERS()}</b>
      {#each team.managers as m, i}
        <a href="/{$page.params.lang}/registry/players/profile?id={m.id}">
          {i == team.managers.length - 1 ? m.name : `${m.name}, `}
        </a>
      {/each}
    </div>
  </div>
  <div class="about_me">
    {team.description}
  </div>
</div>

<style>
  div.wrapper {
    display: inline-grid;
    column-gap: 20px;
    margin: 10px 0;
    grid-template-columns: 1fr 2fr 2fr;
  }
  img.avatar {
    width: 150px;
    height: 150px;
    margin: 10px;
    border: 5px white solid;
    border-radius: 50%;
    object-fit: cover;
  }
  div.team_details {
    grid-column-start: 2;
  }
  div.tag {
    font-size: 2em;
  }
  div.name {
    font-size: 1.5em;
  }
  div.about_me {
    grid-column-start: 3;
  }
</style>
