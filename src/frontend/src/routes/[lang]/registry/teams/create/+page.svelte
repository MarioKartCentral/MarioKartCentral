<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { goto } from '$app/navigation';
  import LL from '$i18n/i18n-svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import ColorSelect from '$lib/components/common/ColorSelect.svelte';
  import LanguageSelect from '$lib/components/common/LanguageSelect.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { permissions, check_permission } from '$lib/util/permissions';
  import LogoUpload from '$lib/components/common/LogoUpload.svelte';
  import Input from '$lib/components/common/Input.svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let tag = "";
  let logo_file = "";

  async function createTeam(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    function getOptionalValue(name: string) {
      return data.get(name) ? data.get(name)?.toString() : '';
    }
    const is_historical = getOptionalValue('is_historical') === 'true';
    const payload = {
      game: data.get('game')?.toString(),
      mode: data.get('mode')?.toString(),
      name: data.get('name')?.toString(),
      tag: data.get('tag')?.toString(),
      color: Number(data.get('color')?.toString()),
      logo_file: logo_file,
      language: data.get('language')?.toString(),
      description: getOptionalValue('description'),
      is_recruiting: getOptionalValue('recruiting') === 'true',
      approval_status: getOptionalValue('approval_status'),
      is_historical: is_historical,
      is_active: !is_historical,
    };
    console.log(payload);
    let endpoint = '/api/registry/teams/request';
    if(check_permission(user_info, permissions.manage_teams)) {
      endpoint = '/api/registry/teams/create';
    }
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
  <Section header={$LL.TEAMS.GENERAL_INFO()}>
    <div class="option">
      <GameModeSelect is_team flex/>
    </div>
    <div class="option">
      <label for="name">{$LL.TEAMS.EDIT.TEAM_NAME()}</label>
      <Input name="name" type="text" required no_white_space maxlength={32}/>
    </div>
    <div class="option">
      <label for="tag">{$LL.TEAMS.EDIT.TEAM_TAG()}</label>
      <Input name="tag" type="text" bind:value={tag} required maxlength={5} no_white_space/>
    </div>    
  </Section>
  <Section header={$LL.TEAMS.EDIT.CUSTOMIZATION()}>
    <div class="option">
      <label for="color">{$LL.TEAMS.EDIT.TEAM_COLOR()}</label>
      <ColorSelect tag={tag}/>
    </div>
    <div class="option">
      <label for="logo">{$LL.TEAMS.EDIT.TEAM_LOGO()}</label>
      <LogoUpload bind:file={logo_file}/>
    </div>
    
  </Section>
  <Section header={$LL.TEAMS.EDIT.MISC_INFO()}>
    <div class="option">
      <label for="language">{$LL.TEAMS.PROFILE.MAIN_LANGUAGE()}</label>
      <LanguageSelect/>
    </div>
    <div class="option">
      <div>
        <label for="description">{$LL.TEAMS.EDIT.TEAM_DESCRIPTION()}</label>
      </div>
      <textarea name="description" maxlength=200/>
    </div>
    <div class="option">
      <label for="recruiting">{$LL.TEAMS.EDIT.RECRUITMENT_STATUS()}</label>
      <select name="recruiting">
        <option value="true">{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.RECRUITING()}</option>
        <option value="false">{$LL.TEAMS.PROFILE.RECRUITMENT_STATUS.NOT_RECRUITING()}</option>
      </select>
    </div>
  </Section>
  {#if check_permission(user_info, permissions.manage_teams)}
    <Section header="Moderator">
      <div class="option">
        <label for="approval_status">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.STATUS()}</label>
        <select name="approval_status">
          <option value="approved">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.APPROVED()}</option>
          <option value="pending">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.PENDING()}</option>
          <option value="denied">{$LL.TEAMS.PROFILE.APPROVAL_STATUS.DENIED()}</option>
        </select>
      </div>
      <div class="option">
        <label for="is_historical">{$LL.TEAMS.PROFILE.ACTIVE_HISTORICAL()}</label>
        <select name="is_historical">
          <option value={false}>{$LL.TEAMS.PROFILE.ACTIVE()}</option>
          <option value={true}>{$LL.TEAMS.PROFILE.HISTORICAL()}</option>
        </select>
      </div>
    </Section>
  {/if}
  <Section header={$LL.COMMON.SUBMIT()}>
    <Button type="submit">{$LL.COMMON.SUBMIT()}</Button>
  </Section>
</form>

<style>
  :global(label) {
    display: inline-block;
    width: 150px;
    margin-right: 10px;
  }
  .option {
    margin-bottom: 10px;
    display: flex;
    align-items: center;
  }
</style>