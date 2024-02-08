<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import { setTeamPerms, team_permissions } from '$lib/util/util';
  import TeamPermissionCheck from '$lib/components/common/TeamPermissionCheck.svelte';
  import LinkButton from '$lib/components/common/LinkButton.svelte';
  import Tag from '$lib/components/registry/teams/Tag.svelte';
  import { colors } from '$lib/stores/colors';
  import LL from '$i18n/i18n-svelte';

  let id = 0;
  let team: Team;

  $: colorsSorted = sortColors();
  $: team_name = team ? team.name : 'Registry';

  setTeamPerms();

  function sortColors() {
    const copyColors: { id: number; label: string; value: string }[] = [];
    for (let i = 0; i < 10; i++) {
      for (let j = i; j < colors.length; j = j + 10) {
        console.log(j);
        copyColors.push(colors[j]);
      }
    }
    return copyColors;
  }

  const languages = [
    { value: 'de', getLang: 'DE' },
    { value: 'en-gb', getLang: 'EN_GB' },
    { value: 'en-us', getLang: 'EN_US' },
    { value: 'fr', getLang: 'FR' },
    { value: 'es', getLang: 'ES' },
    { value: 'ja', getLang: 'JA' },
  ];

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
</script>

<svelte:head>
  <title>{team_name} | Mario Kart Central</title>
</svelte:head>

{#if team}
  <Section header={$LL.TEAM_EDIT.TEAM_PAGE()}>
    <div slot="header_content">
      <LinkButton href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{$LL.TEAM_EDIT.BACK_TO_TEAM()}</LinkButton>
    </div>
  </Section>
  <TeamPermissionCheck team_id={id} permission={team_permissions.edit_team_name_tag}>
    <form method="post" on:submit|preventDefault={editNameTag}>
      <Section header="Team Name/Tag">
        <label for="name">{$LL.TEAM_EDIT.TEAM_NAME()}</label>
        <input name="name" type="text" value={team.name} required />
        <br />
        <label for="tag">{$LL.TEAM_EDIT.TEAM_TAG()}</label>
        <input name="tag" type="text" value={team.tag} required />
        <br />
        <button type="submit">{$LL.TEAM_EDIT.REQUEST_NAME_TAG_CHANGE()}</button>
      </Section>
    </form>
  </TeamPermissionCheck>
  <TeamPermissionCheck team_id={id} permission={team_permissions.edit_team_info}>
    <form method="post" on:submit|preventDefault={editTeam}>
      <Section header={$LL.TEAM_EDIT.CUSTOMIZATION()}>
        <label for="color">{$LL.TEAM_EDIT.TEAM_COLOR()}</label>
        <select name="color" bind:value={team.color}>
          {#each colorsSorted as color}
            <option value={color.id}>{$LL.COLORS[color.label]()}</option>
          {/each}
        </select>
        <Tag {team} />
        <br />
        <label for="logo">{$LL.TEAM_EDIT.TEAM_LOGO()}</label>
        <input name="logo" type="text" value={team.logo} />
      </Section>
      <Section header={$LL.TEAM_EDIT.MISC_INFO()}>
        <label for="language">{$LL.PLAYER_PROFILE.LANGUAGE()}</label>
        <select name="language" value={team.language}>
          {#each languages as language}
            <option value={language.value}>{$LL.LANGUAGES[language.getLang]()}</option>
          {/each}
        </select>
        <br />
        <label for="description">{$LL.TEAM_EDIT.TEAM_DESCRIPTION()}</label>
        <br />
        <textarea name="description" value={team.description} />
        <br />
      </Section>
      <Section header={$LL.PLAYER_PROFILE.SUBMIT()}>
        <button type="submit">{$LL.PLAYER_PROFILE.SUBMIT()}</button>
      </Section>
    </form>
  </TeamPermissionCheck>
{/if}
