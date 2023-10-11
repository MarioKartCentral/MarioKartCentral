<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import type { Team } from '$lib/types/team';
    import Section from '$lib/components/common/Section.svelte';
    import { permissions } from '$lib/util/util';
    import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
    import LinkButton from '$lib/components/common/LinkButton.svelte';
  
    let id = 0;
    let team: Team;
    $: team_name = team ? team.name : 'Registry';
  
    const languages = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];
  
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
    <Section header="Team Page">
        <div slot="header_content">
        <LinkButton href="/{$page.params.lang}/registry/teams/profile?id={team.id}">Back to Team</LinkButton>
        </div>
    </Section>
    <PermissionCheck permission={permissions.manage_teams}>
      <form method="post" on:submit|preventDefault={editTeam}>
        <Section header="Team Name/Tag">
            <label for="name">Team Name</label>
            <input name="name" type="text" value={team.name} required />
            <br />
            <label for="tag">Team Tag</label>
            <input name="tag" type="text" value={team.tag} required />
          </Section>
        <Section header="Customization">
          <label for="color">Team Color</label>
          <select name="color" value={team.color}>
            <option value={0}>0</option>
          </select>
          <br />
          <label for="logo">Team Logo</label>
          <input name="logo" type="text" value={team.logo} />
        </Section>
        <Section header="Misc. Info">
          <label for="language">Language</label>
          <select name="language" value={team.language}>
            {#each languages as language}
              <option value={language}>{language}</option>
            {/each}
          </select>
          <br />
          <label for="description">Team Description</label>
          <br />
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
            <br/>
            <label for="is_historical">Active/Historical</label>
            <select name="historical" value={team.is_historical ? "true" : "false"}>
                <option value="false">Active</option>
                <option value="true">Historical</option>
            </select>
        </Section>
        <Section header="Submit">
          <button type="submit">Submit</button>
        </Section>
      </form>
    </PermissionCheck>
  {/if}
  