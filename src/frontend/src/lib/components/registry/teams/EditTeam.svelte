<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import type { Team } from '$lib/types/team';
    import Section from '$lib/components/common/Section.svelte';
    import { setTeamPerms, team_permissions, permissions } from '$lib/util/util';
    import TeamPermissionCheck from '$lib/components/common/TeamPermissionCheck.svelte';
    import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
    import LinkButton from '$lib/components/common/LinkButton.svelte';
    import LL from '$i18n/i18n-svelte';
    import ColorSelect from '$lib/components/common/ColorSelect.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import LanguageSelect from '$lib/components/common/LanguageSelect.svelte';
    import TeamNameTagRequest from './TeamNameTagRequest.svelte';

    export let is_mod = false;
  
    let id = 0;
    let team: Team;
  
    $: team_name = team ? team.name : 'Registry';
  
    setTeamPerms();
  
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
  
    async function editNameTag(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
      const data = new FormData(event.currentTarget);
      const payload = {
        team_id: id,
        name: data.get('name')?.toString(),
        tag: data.get('tag')?.toString(),
      };
      console.log(payload);
      const endpoint = '/api/registry/teams/requestChange';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (response.status < 300) {
        window.location.reload();
        alert(`Your request to change your team's name/tag has been sent to MKCentral staff for approval.`);
      } else {
        alert(`Editing team failed: ${result['title']}`);
      }
    }
  
    async function editTeam(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
      const data = new FormData(event.currentTarget);
      function getOptionalValue(name: string) {
        return data.get(name) ? data.get(name)?.toString() : '';
      }
      const payload = {
        team_id: id,
        color: Number(data.get('color')?.toString()),
        logo: getOptionalValue('logo'),
        language: data.get('language')?.toString(),
        description: getOptionalValue('description'),
      };
      console.log(payload);
      const endpoint = '/api/registry/teams/edit';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (response.status < 300) {
        window.location.reload();
        alert('Successfully edited team');
      } else {
        alert(`Editing team failed: ${result['title']}`);
      }
    }

    async function forceEditTeam(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    function getOptionalValue(name: string) {
      return data.get(name) ? data.get(name)?.toString() : '';
    }
    const payload = {
      team_id: id,
      name: data.get('name')?.toString(),
      tag: data.get('tag')?.toString(),
      color: Number(data.get('color')?.toString()),
      logo: getOptionalValue('logo'),
      language: data.get('language')?.toString(),
      description: getOptionalValue('description'),
      approval_status: data.get('approval_status'),
      is_historical: getOptionalValue('is_historical') === 'true' ? true : false,
    };
    console.log(payload);
    const endpoint = '/api/registry/teams/forceEdit';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert('Successfully edited team');
    } else {
      alert(`Editing team failed: ${result['title']}`);
    }
  }
  </script>
  
  <svelte:head>
    <title>{team_name} | Mario Kart Central</title>
  </svelte:head>
  
  {#if team}
    <Section header={$LL.TEAM_EDIT.TEAM_PAGE()}>
      <div slot="header_content">
        <LinkButton href="/{$page.params.lang}/registry/teams/profile?id={team.id}"
          >{$LL.TEAM_EDIT.BACK_TO_TEAM()}</LinkButton
        >
      </div>
    </Section>
    {#if !is_mod}
        <TeamPermissionCheck team_id={id} permission={team_permissions.edit_team_name_tag}>
            <Section header="Team Name/Tag">
              <TeamNameTagRequest {team}/>
            </Section>
        </TeamPermissionCheck>
        <TeamPermissionCheck team_id={id} permission={team_permissions.edit_team_info}>
            <form method="post" on:submit|preventDefault={editTeam}>
            <Section header={$LL.TEAM_EDIT.CUSTOMIZATION()}>
                <label for="color">{$LL.TEAM_EDIT.TEAM_COLOR()}</label>
                <ColorSelect name="color" tag={team.tag} bind:color={team.color}/>
                <br />
                <label for="logo">{$LL.TEAM_EDIT.TEAM_LOGO()}</label>
                <input name="logo" type="text" value={team.logo} />
            </Section>
            <Section header={$LL.TEAM_EDIT.MISC_INFO()}>
                <label for="language">{$LL.PLAYER_PROFILE.LANGUAGE()}</label>
                <LanguageSelect bind:language={team.language}/>
                <br />
                <label for="description">{$LL.TEAM_EDIT.TEAM_DESCRIPTION()}</label>
                <textarea name="description" value={team.description} />
                <br />
            </Section>
            <Section header={$LL.PLAYER_PROFILE.SUBMIT()}>
                <Button type="submit">{$LL.PLAYER_PROFILE.SUBMIT()}</Button>
            </Section>
            </form>
        </TeamPermissionCheck>
    {:else}
        <PermissionCheck permission={permissions.manage_teams}>
        <form method="post" on:submit|preventDefault={forceEditTeam}>
          <Section header="Team Name/Tag">
            <label for="name">Team Name</label>
            <input name="name" type="text" value={team.name} required />
            <br />
            <label for="tag">Team Tag</label>
            <input name="tag" type="text" bind:value={team.tag} required />
          </Section>
          <Section header="Customization">
            <label for="color">Team Color</label>
            <ColorSelect bind:color={team.color} tag={team.tag} name="color"/>
            <br />
            <label for="logo">Team Logo</label>
            <input name="logo" type="text" value={team.logo} />
          </Section>
          <Section header="Misc. Info">
            <label for="language">Language</label>
            <LanguageSelect bind:language={team.language}/>
            <br />
            <label for="description">Team Description</label>
            <textarea name="description" value={team.description} />
            <br />
          </Section>
          <Section header="Team Status">
            <label for="approval_status">Approval Status</label>
            <select name="approval_status" value={team.approval_status}>
              <option value="approved">Approved</option>
              <option value="denied">Denied</option>
              <option value="pending">Pending</option>
            </select>
            <br />
            <label for="is_historical">Active/Historical</label>
            <select name="historical" value={team.is_historical ? 'true' : 'false'}>
              <option value="false">Active</option>
              <option value="true">Historical</option>
            </select>
          </Section>
          <Section header="Submit">
            <Button type="submit">Submit</Button>
          </Section>
        </form>
        </PermissionCheck>
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
</style>