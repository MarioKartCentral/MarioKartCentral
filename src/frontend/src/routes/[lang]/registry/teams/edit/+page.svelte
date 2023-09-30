<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import { setTeamPerms, team_permissions } from '$lib/util/util';
  import { goto } from '$app/navigation';
  import TeamPermissionCheck from '$lib/components/common/TeamPermissionCheck.svelte';

  let id = 0;
  let team: Team;
  $: team_name = team ? team.name : 'Registry';

  setTeamPerms();

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
      goto(`/${$page.params.lang}/registry/teams/profile?id=${id}`);
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
      goto(`/${$page.params.lang}/registry/teams/profile?id=${id}`);
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
  <TeamPermissionCheck team_id={id} permission={team_permissions.edit_team_name_tag}>
    <form method="post" on:submit|preventDefault={editNameTag}>
      <Section header="Team Name/Tag">
        <label for="name">Team Name</label>
        <input name="name" type="text" value={team.name} required />
        <br />
        <label for="tag">Team Tag</label>
        <input name="tag" type="text" value={team.tag} required />
        <br />
        <button type="submit">Request Name/Tag Change</button>
      </Section>
    </form>
  </TeamPermissionCheck>
  <TeamPermissionCheck team_id={id} permission={team_permissions.edit_team_info}>
    <form method="post" on:submit|preventDefault={editTeam}>
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
      <Section header="Submit">
        <button type="submit">Submit</button>
      </Section>
    </form>
  </TeamPermissionCheck>
{/if}
