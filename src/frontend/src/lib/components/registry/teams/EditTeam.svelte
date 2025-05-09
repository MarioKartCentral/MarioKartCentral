<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import type { Team } from '$lib/types/team';
    import Section from '$lib/components/common/Section.svelte';
    import { team_permissions, permissions, check_team_permission, check_permission } from '$lib/util/permissions';
    import LL from '$i18n/i18n-svelte';
    import ColorSelect from '$lib/components/common/ColorSelect.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import LanguageSelect from '$lib/components/common/LanguageSelect.svelte';
    import TeamNameTagRequest from './TeamNameTagRequest.svelte';
    import type { UserInfo } from '$lib/types/user-info';
    import { user } from '$lib/stores/stores';
    import LogoUpload from '$lib/components/common/LogoUpload.svelte';
    import Input from '$lib/components/common/Input.svelte';

    export let is_mod = false;
  
    let id = 0;
    let team: Team;
    let working = false;
  
    $: team_name = team ? team.name : $LL.NAVBAR.REGISTRY();

    let logo_file: string | null;
    let remove_logo: boolean;

    let user_info: UserInfo;
    user.subscribe((value) => {
      user_info = value;
    });
  
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
  
    async function editTeam(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
      working = true;
      const data = new FormData(event.currentTarget);
      function getOptionalValue(name: string) {
        return data.get(name) ? data.get(name)?.toString() : '';
      }
      const payload = {
        team_id: id,
        color: Number(data.get('color')?.toString()),
        logo_file: logo_file,
        remove_logo: remove_logo,
        language: data.get('language')?.toString(),
        description: getOptionalValue('description'),
      };
      const endpoint = '/api/registry/teams/edit';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      working = false;
      const result = await response.json();
      if (response.status < 300) {
        window.location.reload();
        alert($LL.TEAMS.EDIT.EDIT_TEAM_SUCCESS());
      } else {
        alert(`${$LL.TEAMS.EDIT.EDIT_TEAM_FAILURE()}: ${result['title']}`);
      }
    }

    async function forceEditTeam(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
      working = true;
      const data = new FormData(event.currentTarget);
      function getOptionalValue(name: string) {
        return data.get(name) ? data.get(name)?.toString() : '';
      }
      const payload = {
        team_id: id,
        name: data.get('name')?.toString(),
        tag: data.get('tag')?.toString(),
        color: Number(data.get('color')?.toString()),
        logo_file: logo_file,
        remove_logo: remove_logo,
        language: data.get('language')?.toString(),
        description: getOptionalValue('description'),
        approval_status: data.get('approval_status'),
        is_historical: getOptionalValue('is_historical') === 'true',
      };
      const endpoint = '/api/registry/teams/forceEdit';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      working = false;
      const result = await response.json();
      if (response.status < 300) {
        window.location.reload();
        alert($LL.TEAMS.EDIT.EDIT_TEAM_SUCCESS());
      } else {
        alert(`${$LL.TEAMS.EDIT.EDIT_TEAM_FAILURE()}: ${result['title']}`);
      }
    }
  </script>
  
  <svelte:head>
    <title>{team_name} | MKCentral</title>
  </svelte:head>
  
  {#if team}
    <Section header={$LL.TEAMS.EDIT.TEAM_PAGE()}>
      <div slot="header_content">
        <Button href="/{$page.params.lang}/registry/teams/profile?id={team.id}"
          >{$LL.TEAMS.EDIT.BACK_TO_TEAM()}</Button
        >
      </div>
    </Section>
    {#if !is_mod}
      {#if check_team_permission(user_info, team_permissions.edit_team_name_tag, id)}
      <Section header={$LL.TEAMS.EDIT.TEAM_NAME_TAG()}>
        <TeamNameTagRequest {team}/>
      </Section>
      {/if}
        
      {#if check_team_permission(user_info, team_permissions.edit_team_info, id)}
        <form method="post" on:submit|preventDefault={editTeam}>
          <Section header={$LL.TEAMS.EDIT.CUSTOMIZATION()}>
              <label for="color">{$LL.TEAMS.EDIT.TEAM_COLOR()}</label>
              <ColorSelect name="color" tag={team.tag} bind:color={team.color}/>
              <br />
              <label for="logo">{$LL.TEAMS.EDIT.TEAM_LOGO()}</label>
              <LogoUpload bind:file={logo_file} bind:logo_url={team.logo} bind:remove_logo={remove_logo}/>
          </Section>
          <Section header={$LL.TEAMS.EDIT.MISC_INFO()}>
              <label for="language">{$LL.COMMON.LANGUAGE()}</label>
              <LanguageSelect bind:language={team.language}/>
              <br />
              <label for="description">{$LL.TEAMS.EDIT.TEAM_DESCRIPTION()}</label>
              <textarea name="description" value={team.description} maxlength=200/>
              <br />
          </Section>
          <Section header={$LL.COMMON.SUBMIT()}>
              <Button {working} type="submit">{$LL.COMMON.SUBMIT()}</Button>
          </Section>
        </form>
      {/if}
    {:else}
      {#if check_permission(user_info, permissions.manage_teams)}
        <form method="post" on:submit|preventDefault={forceEditTeam}>
          <Section header={$LL.TEAMS.EDIT.TEAM_NAME_TAG()}>
            <label for="name">{$LL.TEAMS.EDIT.TEAM_NAME()}</label>
            <Input name="name" type="text" value={team.name} required maxlength={32} no_white_space/>
            <br />
            <label for="tag">{$LL.TEAMS.EDIT.TEAM_TAG()}</label>
            <Input name="tag" type="text" bind:value={team.tag} required maxlength={5} no_white_space/>
          </Section>
          <Section header={$LL.TEAMS.EDIT.CUSTOMIZATION()}>
            <label for="color">{$LL.TEAMS.EDIT.TEAM_COLOR()}</label>
            <ColorSelect bind:color={team.color} tag={team.tag} name="color"/>
            <br />
            <label for="logo">{$LL.TEAMS.EDIT.TEAM_LOGO()}</label>
            <LogoUpload bind:file={logo_file} bind:logo_url={team.logo} bind:remove_logo={remove_logo}/>
          </Section>
          <Section header={$LL.TEAMS.EDIT.MISC_INFO()}>
            <label for="language">{$LL.COMMON.LANGUAGE()}</label>
            <LanguageSelect bind:language={team.language}/>
            <br />
            <label for="description">{$LL.TEAMS.EDIT.TEAM_DESCRIPTION()}</label>
            <textarea name="description" value={team.description} maxlength=200/>
            <br />
          </Section>
          <Section header="Team Status">
            <label for="approval_status">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.STATUS()}</label>
            <select name="approval_status" value={team.approval_status}>
              <option value="approved">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.APPROVED()}</option>
              <option value="denied">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.DENIED()}</option>
              <option value="pending">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.PENDING()}</option>
            </select>
            <br />
            <label for="is_historical">{$LL.TEAMS.PROFILE.ACTIVE_HISTORICAL()}</label>
            <select name="is_historical" value={team.is_historical ? 'true' : 'false'}>
              <option value="false">{$LL.TEAMS.PROFILE.ACTIVE()}</option>
              <option value="true">{$LL.TEAMS.PROFILE.HISTORICAL()}</option>
            </select>
          </Section>
          <Section header={$LL.COMMON.SUBMIT()}>
            <Button {working} type="submit">{$LL.TEAMS.PROFILE.EDIT_TEAM()}</Button>
          </Section>
        </form>
      {/if}
    {/if}
  {/if}
  
<style>
    label {
        width: 125px;
        display: inline-block;
    }
    :global(select, input, textarea) {
        width: 200px;
    }
    textarea {
      width: 100%;
      height: 150px;
    }
</style>