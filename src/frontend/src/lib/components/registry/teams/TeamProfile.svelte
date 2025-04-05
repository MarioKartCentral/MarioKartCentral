<script lang="ts">
  import type { Team } from '$lib/types/team';
  import logo from '$lib/assets/logo.png';
  import { LL, locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import { Avatar } from 'flowbite-svelte';

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
  
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const language_strings: any = $LL.LANGUAGES;
</script>

<div class="wrapper">
  <div class="avatar">
    <Avatar size="xl" src={avatar_url} border alt={team.name}/>
  </div>
  <div class="team_details">
    <div class="tag">
      <TagBadge tag={team.tag} color={team.color}/>
    </div>
    <div class="name">
      <b>{team.name}</b>
    </div>
    <div>
      <b>{$LL.TEAMS.PROFILE.REGISTERED()}</b>
      {new Date(team.creation_date * 1000).toLocaleString($locale, options)}
    </div>
    <div>
      <b>{$LL.TEAMS.PROFILE.MAIN_LANGUAGE()}</b>
      {language_strings[team.language.toUpperCase().replace("-", "_")]()}
    </div>
    {#if team.managers.length}
      <div>
        <b>{$LL.TEAMS.PROFILE.MANAGERS()}</b>
        {#each team.managers as m, i}
          <a href="/{$page.params.lang}/registry/players/profile?id={m.id}">
            {i == team.managers.length - 1 ? m.name : `${m.name}, `}
          </a>
        {/each}
      </div>
    {/if}
  </div>
  <div class="about_me">
    {team.description}
  </div>
</div>

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
  div.team_details {
    display: flex;
    flex-direction: column;
    justify-content: center;
    grid-column-start: 2;
    @media(min-width:800px) {
      justify-content: left;
    }
  }
  div.tag {
    font-size: 2em;
  }
  div.name {
    font-size: 1.5em;
  }
  div.about_me {
    display: flex;
    align-self: flex-start;
    grid-column-start: 3;
    justify-content: center;
    max-width: 400px;
    word-break: break-word;
    white-space: pre-line;
    max-height: 200px;
    overflow: hidden;
    @media(min-width: 800px) {
      justify-content: left;
      margin-left: auto;
      margin-right: auto;
    }
  }
  div.avatar { 
    min-width: 150px;
    margin-bottom: 20px;
  }
</style>
