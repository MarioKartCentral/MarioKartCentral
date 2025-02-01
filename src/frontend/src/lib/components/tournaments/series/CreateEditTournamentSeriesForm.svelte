<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { CreateTournamentSeries } from '$lib/types/tournaments/series/create/create-tournament-series';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import MarkdownTextArea from '$lib/components/common/MarkdownTextArea.svelte';
  import LL from '$i18n/i18n-svelte';

  export let series_id: number | null = null;
  export let is_edit = false;

  let data: CreateTournamentSeries = {
    series_id: null,
    series_name: '',
    url: null,
    organizer: 'MKCentral',
    location: null,
    display_order: 0,
    game: 'mk8dx',
    mode: '150cc',
    is_historical: false,
    is_public: true,
    description: '',
    ruleset: '',
    logo: null,
  };

  onMount(async () => {
    if (!series_id) {
      return;
    }
    const res = await fetch(`/api/tournaments/series/${series_id}`);
    if (res.status === 200) {
      const body: CreateTournamentSeries = await res.json();
      data = Object.assign(data, body);
    }
  });

  function updateData() {
    data = data;
  }
  async function createSeries() {
    let payload = data;
    console.log(payload);
    const endpoint = '/api/tournaments/series/create';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      goto(`/${$page.params.lang}/tournaments/series`);
      alert($LL.TOURNAMENTS.SERIES.CREATE_SERIES_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.SERIES.CREATE_SERIES_FAILED()}: ${result['title']}`);
    }
  }
  async function editSeries() {
    data.series_id = series_id;
    let payload = data;
    console.log(payload);
    const endpoint = `/api/tournaments/series/${series_id}/edit`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      goto(`/${$page.params.lang}/tournaments/series/details?id=${series_id}`);
      alert($LL.TOURNAMENTS.SERIES.EDIT_SERIES_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.SERIES.EDIT_SERIES_FAILED()}: ${result['title']}`);
    }
  }
</script>

<form method="POST" on:submit|preventDefault={is_edit ? editSeries : createSeries}>
  <Section header={is_edit ? $LL.TOURNAMENTS.SERIES.EDIT_TOURNAMENT_SERIES() : $LL.TOURNAMENTS.SERIES.CREATE_TOURNAMENT_SERIES()}>
    <div slot="header_content">
      {#if series_id}
        <Button href="/{$page.params.lang}/tournaments/series/details?id={series_id}">{$LL.TOURNAMENTS.SERIES.BACK_TO_SERIES()}</Button>
      {/if}
    </div>
    <div class="option">
      <div>
        <label for="series_name">{$LL.TOURNAMENTS.SERIES.SERIES_NAME()}</label>
      </div>
      <div>
        <input type="text" name="series_name" bind:value={data.series_name} minlength="1" required />
      </div>
    </div>
    <div class="option">
      <div>
        <label for="url">{$LL.TOURNAMENTS.SERIES.SERIES_URL()}</label>
      </div>
      <div>
        <input type="text" name="url" bind:value={data.url} />
      </div>
    </div>
    <div class="option">
      <div>
        <label for="display_order">{$LL.TOURNAMENTS.SERIES.DISPLAY_ORDER()}</label>
      </div>
      <div>
        <input type="number" name="display_order" bind:value={data.display_order} min="0" required />
      </div>
    </div>
    <div class="logo">
      <div>
        <label for="logo">{$LL.TOURNAMENTS.SERIES.SERIES_LOGO()}</label>
      </div>
      <div>
        <input type="text" name="logo" bind:value={data.logo} />
      </div>
    </div>
  </Section>
  <Section header={$LL.TOURNAMENTS.SERIES.EVENT_DEFAULTS()}>
    <div class="option">
      <div>
        <label for="organizer">{$LL.TOURNAMENTS.MANAGE.ORGANIZED_BY()}</label>
      </div>
      <div>
        <select name="organizer" bind:value={data.organizer} on:change={updateData}>
          <option value="MKCentral">{$LL.TOURNAMENTS.MANAGE.ORGANIZED_BY_MKCENTRAL()}</option>
          <option value="Affiliate">{$LL.TOURNAMENTS.MANAGE.ORGANIZED_BY_AFFILIATE()}</option>
          <option value="LAN">{$LL.TOURNAMENTS.MANAGE.ORGANIZED_BY_LAN()}</option>
        </select>
      </div>
    </div>
    {#if data.organizer === 'LAN'}
      <div class="option">
        <div>
          <label for="location">{$LL.TOURNAMENTS.MANAGE.LOCATION()}</label>
        </div>
        <div>
          <input name="location" type="text" bind:value={data.location} />
        </div>
      </div>
    {/if}
    <div class="option">
      <GameModeSelect bind:game={data.game} bind:mode={data.mode} />
    </div> 
  </Section>
  <Section header={$LL.TOURNAMENTS.SERIES.SERIES_DESCRIPTION()}>
    <div class="option">
      <MarkdownTextArea name="description" bind:value={data.description} on:change={updateData}/>
    </div>
  </Section>
  <Section header={$LL.TOURNAMENTS.SERIES.SERIES_RULESET()}>
    <div class="option">
      <MarkdownTextArea name="ruleset" bind:value={data.ruleset} on:change={updateData}/>
    </div>
  </Section>
  <Section header={$LL.TOURNAMENTS.SERIES.VISIBILITY()}>
    <div class="option">
      <div>
        <label for="is_public">{$LL.TOURNAMENTS.SERIES.SHOW_ON_SERIES_LISTING()}</label>
      </div>
      <div>
        <select name="is_public" bind:value={data.is_public}>
          <option value={true}>{$LL.COMMON.SHOW()}</option>
          <option value={false}>{$LL.COMMON.HIDE()}</option>
        </select>
      </div>
    </div>
    <div class="option">
      <div>
        <label for="is_historical">{$LL.TOURNAMENTS.SERIES.ACTIVE_HISTORICAL()}</label>
      </div>
      <div>
        <select name="is_historical" bind:value={data.is_historical}>
          <option value={false}>{$LL.TOURNAMENTS.SERIES.ACTIVE()}</option>
          <option value={true}>{$LL.TOURNAMENTS.SERIES.HISTORICAL()}</option>
        </select>
      </div>
    </div>
  </Section>
  <Section header={$LL.COMMON.SUBMIT()}>
    <Button type="submit">{is_edit ? $LL.TOURNAMENTS.SERIES.EDIT() : $LL.TOURNAMENTS.SERIES.CREATE()}</Button>
  </Section>
</form>

<style>
  div.option {
    margin-bottom: 10px;
  }
</style>
