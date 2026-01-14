<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import TeamRosterManage from '$lib/components/registry/teams/TeamRosterManage.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import LL from '$i18n/i18n-svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_team_permission, team_permissions } from '$lib/util/permissions';
  import { sortFilterRosters } from '$lib/util/util';
  import Input from '$lib/components/common/Input.svelte';
  import ColorSelect from '$lib/components/common/ColorSelect.svelte';

  export let is_mod = false;

  let id = 0;
  let team: Team;
  $: team_name = team ? team.name : 'Registry';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let working = false;

  let createParams = {
    name: null,
    game: null,
    mode: null,
    tag: null,
    color: undefined,
    is_recruiting: true,
  };

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/registry/teams/${id}`);
    if (res.status != 200) {
      return;
    }
    const body: Team = await res.json();
    team = body;
  });

  async function createRoster() {
    working = true;
    const payload = {
      team_id: team.id,
      ...createParams,
    };
    const endpoint = '/api/registry/teams/requestCreateRoster';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert('Your roster has been sent to MKCentral staff for approval.');
    } else {
      alert(`Creating roster failed: ${result['title']}`);
    }
  }
</script>

<svelte:head>
  <title>{team_name} | MKCentral</title>
</svelte:head>

{#if team}
  <Section header={$LL.TEAMS.EDIT.TEAM_PAGE()}>
    <div slot="header_content">
      <Button href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{$LL.TEAMS.EDIT.BACK_TO_TEAM()}</Button>
    </div>
  </Section>
  {#if check_team_permission(user_info, team_permissions.manage_rosters, id)}
    {#each sortFilterRosters(team.rosters, is_mod) as roster (roster.id)}
      <TeamRosterManage {roster} {is_mod} />
    {/each}
  {/if}
  {#if check_team_permission(user_info, team_permissions.create_rosters, id)}
    <Section header={$LL.TEAMS.EDIT.NEW_ROSTER()}>
      <form method="post" on:submit|preventDefault={createRoster}>
        <GameModeSelect
          required
          is_team
          bind:game={createParams.game}
          bind:mode={createParams.mode}
          containerClass="mb-[10px] sm:flex sm:items-center"
        />
        <div class="option sm:flex sm:items-center">
          <label for="name">{$LL.TEAMS.EDIT.ROSTER_NAME()}</label>
          <div>
            <Input name="name" type="text" required maxlength={32} no_white_space bind:value={createParams.name} />
          </div>
        </div>
        <div class="option sm:flex sm:items-center">
          <label for="tag">{$LL.TEAMS.EDIT.ROSTER_TAG()}</label>
          <div>
            <Input name="tag" type="text" required maxlength={8} bind:value={createParams.tag} />
          </div>
        </div>
        <div class="option sm:flex sm:items-center">
          <label for="new-roster-color-select">{$LL.TEAMS.EDIT.TEAM_COLOR()}</label>
          <ColorSelect
            id="new-roster-color-select"
            name="color"
            bind:tag={createParams.tag}
            bind:color={createParams.color}
          />
        </div>
        <div class="option sm:flex sm:items-center">
          <label for="recruiting">{$LL.TEAMS.EDIT.RECRUITMENT_STATUS()}</label>
          <div>
            <select name="recruiting" bind:value={createParams.is_recruiting}>
              <option value={true}>{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.RECRUITING()}</option>
              <option value={false}>{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.NOT_RECRUITING()}</option>
            </select>
          </div>
        </div>
        <div>
          <Button type="submit" {working}>{$LL.COMMON.SUBMIT()}</Button>
        </div>
      </form>
    </Section>
  {/if}
{/if}

<style>
  :global(label) {
    display: inline-block;
    width: 150px;
    margin-right: 10px;
  }
  .option {
    margin-bottom: 10px;
  }
</style>
