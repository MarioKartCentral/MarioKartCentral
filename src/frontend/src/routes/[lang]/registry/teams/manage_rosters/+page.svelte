<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import { setTeamPerms, team_permissions } from '$lib/util/util';
  import TeamPermissionCheck from '$lib/components/common/TeamPermissionCheck.svelte';
  import TeamRosterManage from '$lib/components/registry/teams/TeamRosterManage.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import LinkButton from '$lib/components/common/LinkButton.svelte';

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

  let game = 'mk8dx';
  let mode = '150cc';

  async function createRoster(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    function getOptionalValue(name: string) {
      return data.get(name) ? data.get(name)?.toString() : '';
    }
    const payload = {
      team_id: team.id,
      game: data.get('game')?.toString(),
      mode: data.get('mode')?.toString(),
      name: data.get('name')?.toString(),
      tag: data.get('tag')?.toString(),
      is_recruiting: getOptionalValue('recruiting') === 'true' ? true : false,
    };
    console.log(payload);
    const endpoint = '/api/registry/teams/requestCreateRoster';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert('Your roster has been sent to MKCentral staff for approval.');
    } else {
      alert(`Creating roster failed: ${result['title']}`);
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
  <TeamPermissionCheck team_id={id} permission={team_permissions.manage_rosters}>
    {#each team.rosters.filter((r) => r.approval_status !== 'denied') as roster}
      <TeamRosterManage {roster} />
    {/each}
  </TeamPermissionCheck>
  <TeamPermissionCheck team_id={id} permission={team_permissions.create_rosters}>
    <Section header="New Roster">
      <form method="post" on:submit|preventDefault={createRoster}>
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
        <label for="name">Roster Name</label>
        <input name="name" type="text" required />
        <br />
        <label for="tag">Roster Tag</label>
        <input name="tag" type="text" required />
        <label for="recruiting">Recruitment Status</label>
        <select name="recruiting">
          <option value="true">Recruiting</option>
          <option value="false">Not Recruiting</option>
        </select>
        <div>
          <button type="submit">Submit</button>
        </div>
      </form>
    </Section>
  </TeamPermissionCheck>
{/if}
