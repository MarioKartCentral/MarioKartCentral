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

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let tag = "";

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
      logo: getOptionalValue('logo'),
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
    window.confirm(endpoint);
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
    <div class="option">
      <label for="color">{$LL.TEAM_EDIT.TEAM_COLOR()}</label>
      <ColorSelect tag={tag}/>
    </div>
    <div class="option">
      <label for="logo">{$LL.TEAM_EDIT.TEAM_LOGO()}</label>
      <input name="logo" type="text" />
    </div>
    
  </Section>
  <Section header={$LL.TEAM_EDIT.MISC_INFO()}>
    <div class="option">
      <label for="language">{$LL.TEAM_PROFILE.MAIN_LANGUAGE()}</label>
      <LanguageSelect/>
    </div>
    <div class="option">
      <div>
        <label for="description">{$LL.TEAM_EDIT.TEAM_DESCRIPTION()}</label>
      </div>
      <textarea name="description" />
    </div>
    <div class="option">
      <label for="recruiting">{$LL.TEAM_EDIT.RECRUITMENT_STATUS()}</label>
      <select name="recruiting">
        <option value="true">{$LL.TEAM_PROFILE.RECRUITMENT_STATUS.RECRUITING()}</option>
        <option value="false">{$LL.TEAM_PROFILE.RECRUITMENT_STATUS.NOT_RECRUITING()}</option>
      </select>
    </div>
  </Section>
  {#if check_permission(user_info, permissions.manage_teams)}
    <Section header="Moderator">
      <div class="option">
        <label for="approval_status">{$LL.TEAM_PROFILE.APPROVAL_STATUS.STATUS()}</label>
        <select name="approval_status">
          <option value="approved">{$LL.TEAM_PROFILE.APPROVAL_STATUS.APPROVED()}</option>
          <option value="pending">{$LL.TEAM_PROFILE.APPROVAL_STATUS.PENDING()}</option>
          <option value="denied">{$LL.TEAM_PROFILE.APPROVAL_STATUS.DENIED()}</option>
        </select>
      </div>
      <div class="option">
        <label for="is_historical">{$LL.TEAM_PROFILE.ACTIVE_HISTORICAL()}</label>
        <select name="is_historical">
          <option value={false}>{$LL.TEAM_PROFILE.ACTIVE()}</option>
          <option value={true}>{$LL.TEAM_PROFILE.HISTORICAL()}</option>
        </select>
      </div>
    </Section>
  {/if}
  <Section header={$LL.SUBMIT()}>
    <Button type="submit">{$LL.SUBMIT()}</Button>
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