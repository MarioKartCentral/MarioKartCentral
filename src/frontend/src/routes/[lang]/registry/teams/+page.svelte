<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import TeamList from '$lib/components/registry/teams/TeamList.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import LL from '$i18n/i18n-svelte';
  import { check_permission, permissions } from '$lib/util/permissions';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  let teams: Team[] = [];
  
  let filters = {
    game: null,
    mode: null,
    name: null
  }

  async function fetchData() {
    teams = [];
    let url = '/api/registry/teams?is_historical=false';
    if (filters.game) {
      url += `&game=${filters.game}`;
    }
    if(filters.mode) {
      url += `&mode=${filters.mode}`;
    }
    if(filters.name) {
      url += `&name=${filters.name}`;
    }
    const res = await fetch(url);
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        teams.push(t);
      }
      teams = teams;
    }
  }

  onMount(async () => {
    fetchData();
  });
</script>

<Section header={$LL.TEAM_LIST.TEAM_LISTING()}>
  <div slot="header_content">
    {#if user_info.player_id && check_permission(user_info, permissions.create_team, true)}
      <Button href="/{$page.params.lang}/registry/teams/create">{$LL.TEAM_LIST.CREATE_TEAM()}</Button>
    {/if}
  </div>
  <form on:submit|preventDefault={fetchData}>
    <div class="flex">
      <GameModeSelect all_option hide_labels inline bind:game={filters.game} bind:mode={filters.mode}/>
      <div class="option">
        <input class="search" bind:value={filters.name} type="text" placeholder="Search by team or roster name..."/>
      </div>
      <div class="option">
        <Button type="submit">Search</Button>
      </div>
    </div>
  </form>
  
  {teams.length}
  {$LL.TEAM_LIST.TEAMS()}
  <TeamList {teams} />
</Section>

<style>
  .flex {
    width: 100%;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }
  .option {
    margin-bottom: 10px;
    margin-right: 10px;
  }
  input {
    width: 250px;
  }
</style>
