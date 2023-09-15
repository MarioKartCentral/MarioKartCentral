<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { goto } from '$app/navigation';

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
  const languages = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];

  let game = 'mk8dx';
  let mode = '150cc';

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
  <Section header="General Info">
    <label for="game">Game</label>
    <select name="game" bind:value={game} on:change={() => ([mode] = valid_modes[game])}>
      {#each Object.keys(valid_games) as game}
        <option value={game}>{valid_games[game]}</option>
      {/each}
    </select>
    <label for="mode">Mode</label>
    <select name="mode" bind:value={mode}>
      {#each valid_modes[game] as mode}
        <option value={mode}>{mode_names[mode]}</option>
      {/each}
    </select>
    <br />
    <label for="name">Team Name</label>
    <input name="name" type="text" required />
    <br />
    <label for="tag">Team Tag</label>
    <input name="tag" type="text" required />
  </Section>
  <Section header="Customization">
    <label for="color">Team Color</label>
    <select name="color">
      <option value={0}>0</option>
    </select>
    <br />
    <label for="logo">Team Logo</label>
    <input name="logo" type="text" />
  </Section>
  <Section header="Misc. Info">
    <label for="language">Language</label>
    <select name="language">
      {#each languages as language}
        <option value={language}>{language}</option>
      {/each}
    </select>
    <br />
    <label for="description">Team Description</label>
    <br />
    <textarea name="description" />
    <br />
    <label for="recruiting">Recruitment Status</label>
    <select name="recruiting">
      <option value="true">Recruiting</option>
      <option value="false">Not Recruiting</option>
    </select>
  </Section>
  <Section header="Submit">
    <button type="submit">Submit</button>
  </Section>
</form>
