<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { goto } from '$app/navigation';
  import LL from '$i18n/i18n-svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import ColorSelect from '$lib/components/common/ColorSelect.svelte';

  const languages = [
    { value: 'de', getLang: 'DE' },
    { value: 'en-gb', getLang: 'EN_GB' },
    { value: 'en-us', getLang: 'EN_US' },
    { value: 'fr', getLang: 'FR' },
    { value: 'es', getLang: 'ES' },
    { value: 'ja', getLang: 'JA' },
  ];
  let tag = "";

  async function createTeam(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    function getOptionalValue(name: string) {
      return data.get(name) ? data.get(name)?.toString() : '';
    }
    const payload = {
      game: data.get('game')?.toString(),
      mode: data.get('mode')?.toString(),
      name: data.get('name')?.toString(),
      tag: data.get('tag')?.toString(),
      color: Number(data.get('color')?.toString()),
      logo: getOptionalValue('logo'),
      language: data.get('language')?.toString(),
      description: getOptionalValue('description'),
      is_recruiting: getOptionalValue('recruiting') === 'true' ? true : false,
    };
    console.log(payload);
    const endpoint = '/api/registry/teams/request';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      let team_id = result['id'];
      if(team_id) {
        goto(`/${$page.params.lang}/registry/teams/profile?id=${team_id}`);
      }
      else {
        goto(`/${$page.params.lang}/registry/teams`);
      }
      alert('Your team has been sent to MKCentral staff for approval.');
    } else {
      alert(`Creating team failed: ${result['title']}`);
    }
  }
</script>

<form method="post" on:submit|preventDefault={createTeam}>
  <Section header={$LL.TEAM_CREATE.GENERAL_INFO()}>
    <GameModeSelect is_team flex/>
    <div class="option">
      <label for="name">{$LL.TEAM_EDIT.TEAM_NAME()}</label>
      <input name="name" type="text" required pattern="^\S.*\S$|^\S$"/>
    </div>
    <div class="option">
      <label for="tag">{$LL.TEAM_EDIT.TEAM_TAG()}</label>
      <input name="tag" type="text" bind:value={tag} required maxlength=5 pattern="^\S.*\S$|^\S$"/>
    </div>    
  </Section>
  <Section header={$LL.TEAM_EDIT.CUSTOMIZATION()}>
    <label for="color">{$LL.TEAM_EDIT.TEAM_COLOR()}</label>
    <ColorSelect tag={tag}/>
    <br />
    <label for="logo">{$LL.TEAM_EDIT.TEAM_LOGO()}</label>
    <input name="logo" type="text" />
  </Section>
  <Section header={$LL.TEAM_EDIT.MISC_INFO()}>
    <label for="language">{$LL.TEAM_PROFILE.MAIN_LANGUAGE()}</label>
    <select name="language" value="en-us">
      {#each languages as language}
        <option value={language.value}>{$LL.LANGUAGES[language.getLang]()}</option>
      {/each}
    </select>
    <br />
    <label for="description">{$LL.TEAM_EDIT.TEAM_DESCRIPTION()}</label>
    <br />
    <textarea name="description" />
    <br />
    <label for="recruiting">{$LL.TEAM_EDIT.RECRUITMENT_STATUS()}</label>
    <select name="recruiting">
      <option value="true">{$LL.TEAM_PROFILE.RECRUITMENT_STATUS.RECRUITING()}</option>
      <option value="false">{$LL.TEAM_PROFILE.RECRUITMENT_STATUS.NOT_RECRUITING()}</option>
    </select>
  </Section>
  <Section header={$LL.PLAYER_PROFILE.SUBMIT()}>
    <Button type="submit">{$LL.PLAYER_PROFILE.SUBMIT()}</Button>
  </Section>
</form>

<style>
  :global(label) {
    display: inline-block;
    width: 150px;
    margin-right: 10px;
  }
  input {
    width: 200px;
  }
  .option {
    margin-bottom: 10px;
    display: flex;
    align-items: center;
  }
</style>