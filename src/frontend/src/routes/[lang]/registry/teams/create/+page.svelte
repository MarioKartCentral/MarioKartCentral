<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { goto } from '$app/navigation';
  import Tag from '$lib/components/registry/teams/Tag.svelte';
  import LL from '$i18n/i18n-svelte';
  import { colors } from '$lib/util/util';

  const valid_games: { [key: string]: string } = {
    mk8dx: 'Mario Kart 8 Deluxe',
    mkw: 'Mario Kart Wii',
    mkt: 'Mario Kart Tour',
  };
  const valid_modes: { [key: string]: string[] } = { mk8dx: ['150cc', '200cc'], mkw: ['rt', 'ct'], mkt: ['vsrace'] };
  const mode_names: { [key: string]: string } = {
    '150cc': '150cc',
    '200cc': '200cc',
    rt: 'Regular Tracks',
    ct: 'Custom Tracks',
    vsrace: 'VS Race',
  };
  const languages = [
    { value: 'de', getLang: 'DE' },
    { value: 'en-gb', getLang: 'EN_GB' },
    { value: 'en-us', getLang: 'EN_US' },
    { value: 'fr', getLang: 'FR' },
    { value: 'es', getLang: 'ES' },
    { value: 'ja', getLang: 'JA' },
  ];
  let game = 'mk8dx';
  let mode = '150cc';
  let color = { id: 1 };

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
      goto(`/`);
      alert('Your team has been sent to MKCentral staff for approval.');
    } else {
      alert(`Creating team failed: ${result['title']}`);
    }
  }
</script>

<form method="post" on:submit|preventDefault={createTeam}>
  <Section header={$LL.TEAM_CREATE.GENERAL_INFO()}>
    <label for="game">{$LL.TEAM_LIST.GAME()}</label>
    <select name="game" bind:value={game} on:change={() => ([mode] = valid_modes[game])}>
      {#each Object.keys(valid_games) as game}
        <option value={game}>{valid_games[game]}</option>
      {/each}
    </select>
    <label for="mode">{$LL.TEAM_LIST.MODE()}</label>
    <select name="mode" bind:value={mode}>
      {#each valid_modes[game] as mode}
        <option value={mode}>{mode_names[mode]}</option>
      {/each}
    </select>
    <br />
    <label for="name">{$LL.TEAM_EDIT.TEAM_NAME()}</label>
    <input name="name" type="text" required />
    <br />
    <label for="tag">{$LL.TEAM_EDIT.TEAM_TAG()}</label>
    <input name="tag" type="text" required />
  </Section>
  <Section header={$LL.TEAM_EDIT.CUSTOMIZATION()}>
    <label for="color">{$LL.TEAM_EDIT.TEAM_COLOR()}</label>
    <select name="color" bind:value={color.id}>
      {#each colors as color, i}
        <option value={i+1}>{$LL.COLORS[color.label]()}</option>
      {/each}
    </select>
    <Tag team={{ color: color.id, tag: ' ' }} />
    <br />
    <label for="logo">{$LL.TEAM_EDIT.TEAM_LOGO()}</label>
    <input name="logo" type="text" />
  </Section>
  <Section header={$LL.TEAM_EDIT.MISC_INFO()}>
    <label for="language">{$LL.LANGUAGE()}</label>
    <select name="language">
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
    <button type="submit">{$LL.PLAYER_PROFILE.SUBMIT()}</button>
  </Section>
</form>
