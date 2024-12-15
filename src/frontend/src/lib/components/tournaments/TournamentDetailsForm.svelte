<script lang="ts">
  import type { CreateTournament } from '$lib/types/tournaments/create/create-tournament';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import Section from '../common/Section.svelte';
  import SeriesSearch from '../common/SeriesSearch.svelte';
  import GameModeSelect from '../common/GameModeSelect.svelte';
  import MarkdownTextArea from '../common/MarkdownTextArea.svelte';
  import LL from '$i18n/i18n-svelte';

  export let data: CreateTournament;
  export let update_function: () => void; // function used to update data in the parent component
  export let series_restrict = false; // if we want to lock us into a specific series
  export let is_template = false; // used to get rid of dates stuff for template creation/edit pages
  export let is_edit = false; // only use when editing tournaments, not needed for templates

  let series: TournamentSeries | null;

  function getDateTimeLocal(n: number | null) {
    if (!n) {
      return;
    }
    let d = new Date(n * 1000);
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    let r = d.toISOString().slice(0, 16);
    return r;
  }

  function updateData() {
    if (data.organizer != 'LAN') {
      data.location = null;
    }
    if (data.teams_allowed) {
      data.mii_name_required = false;
      data.host_status_required = false;
      data.require_single_fc = false;
      data.squad_tag_required = true;
      data.squad_name_required = true;
      data.checkins_enabled = false;
      if (!data.teams_only) {
        data.team_members_only = false;
        data.min_representatives = null;
      }
    } else {
      data.teams_only = false;
      data.team_members_only = false;
    }
    if (!data.is_squad) {
      data.min_squad_size = null;
      data.max_squad_size = null;
      data.squad_tag_required = false;
      data.squad_name_required = false;
      data.teams_allowed = false;
      data.teams_only = false;
      data.team_members_only = false;
      data.min_representatives = null;
    }
    if (!data.checkins_enabled) {
      data.checkins_open = false;
      data.min_players_checkin = null;
    }
    if (!data.series_id) {
      data.use_series_description = false;
      data.use_series_ruleset = false;
      data.series_stats_include = false;
      data.use_series_logo = false;
    }
    if (data.use_series_logo) {
      data.logo = null;
    }
    if (data.game !== 'mkw' || !data.is_squad) {
      data.bagger_clause_enabled = false;
    }
    update_function();
  }
</script>

<Section header={$LL.TOURNAMENTS.MANAGE.TOURNAMENT_DETAILS()}>
  <div class="option">
    <div>
      <label for="tournament_name">{$LL.TOURNAMENTS.MANAGE.TOURNAMENT_NAME_REQUIRED()}</label>
    </div>
    <div>
      <input name="tournament_name" class="tournament_name" type="text" bind:value={data.name} minlength="1" required />
    </div>
  </div>
  <div class="option">
    <div>
      <label for="tournament_series">{$LL.TOURNAMENTS.TOURNAMENT_SERIES()}</label>
    </div>
    <div>
      <SeriesSearch
        bind:option={series}
        bind:series_id={data.series_id}
        lock={series_restrict}
        on:change={updateData}
      />
    </div>
  </div>
  {#if !is_template}
    <div class="option">
      <div>
        <label for="date_start">{$LL.TOURNAMENTS.MANAGE.START_DATE()}</label>
      </div>
      <div>
        <input name="date_start" type="datetime-local" value={getDateTimeLocal(data.date_start)} required />
      </div>
    </div>
    <div class="option">
      <div>
        <label for="date_end">{$LL.TOURNAMENTS.MANAGE.END_DATE()}</label>
      </div>
      <div>
        <input name="date_end" type="datetime-local" value={getDateTimeLocal(data.date_end)} required />
      </div>
    </div>
  {/if}
  {#if series}
    <div class="option">
      <div>
        <label for="use_series_logo">{$LL.TOURNAMENTS.MANAGE.USE_SERIES_LOGO()}</label>
      </div>
      <div>
        <select name="use_series_logo" bind:value={data.use_series_logo} on:change={updateData}>
          <option value={false}>{$LL.NO()}</option>
          <option value={true}>{$LL.YES()}</option>
        </select>
      </div>
    </div>
  {/if}
  {#if !data.use_series_logo}
    <div class="option">
      <div>
        <label for="logo">{$LL.TOURNAMENTS.MANAGE.LOGO()}</label>
      </div>
      <div>
        <input name="logo" type="text" bind:value={data.logo} />
      </div>
    </div>
  {/if}
</Section>
<Section header={$LL.TOURNAMENTS.MANAGE.TOURNAMENT_FORMAT()}>
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
  <GameModeSelect bind:game={data.game} bind:mode={data.mode} on:change={updateData} disabled={is_edit} />
  <div class="option">
    <div>
      <label for="is_squad">{$LL.TOURNAMENTS.MANAGE.REGISTRATION_FORMAT()}</label>
    </div>
    <div>
      <select name="is_squad" bind:value={data.is_squad} on:change={updateData} disabled={is_edit}>
        <option value={false}>{$LL.TOURNAMENTS.MANAGE.REGISTRATION_FORMAT_SOLO()}</option>
        <option value={true}>{$LL.TOURNAMENTS.MANAGE.REGISTRATION_FORMAT_SQUAD()}</option>
      </select>
    </div>
  </div>
  {#if data.is_squad}
    <div class="indented">
      <div class="option">
        <div>
          <label for="min_squad_size">{$LL.TOURNAMENTS.MANAGE.MINIMUM_PLAYERS()}</label>
        </div>
        <div>
          <input class="number" type="number" name="min_squad_size" min="1" max="99" bind:value={data.min_squad_size} />
        </div>
      </div>
      <div class="option">
        <div>
          <label for="max_squad_size">{$LL.TOURNAMENTS.MANAGE.MAXIMUM_PLAYERS()}</label>
        </div>
        <div>
          <input class="number" type="number" name="max_squad_size" min="1" max="99" bind:value={data.max_squad_size} />
        </div>
      </div>
      <div class="option">
        <div>
          <label for="squad_tag_required">{$LL.TOURNAMENTS.MANAGE.SQUAD_TAG_REQUIRED()}</label>
        </div>
        <div>
          <select
            name="squad_tag_required"
            bind:value={data.squad_tag_required}
            on:change={updateData}
            disabled={is_edit || data.teams_allowed}
          >
            <option value={false}>{$LL.NO()}</option>
            <option value={true}>{$LL.YES()}</option>
          </select>
        </div>
      </div>
      <div class="option">
        <div>
          <label for="squad_name_required">{$LL.TOURNAMENTS.MANAGE.SQUAD_NAME_REQUIRED()}</label>
        </div>
        <div>
          <select
            name="squad_name_required"
            bind:value={data.squad_name_required}
            on:change={updateData}
            disabled={is_edit || data.teams_allowed}
          >
            <option value={false}>{$LL.NO()}</option>
            <option value={true}>{$LL.YES()}</option>
          </select>
        </div>
      </div>
      {#if data.game === 'mkw'}
        <div class="option">
          <div>
            <label for="bagger_clause_enabled">{$LL.TOURNAMENTS.MANAGE.BAGGER_CLAUSE_ENABLED()}</label>
          </div>
          <div>
            <select
              name="bagger_clause_enabled"
              bind:value={data.bagger_clause_enabled}
              on:change={updateData}
              disabled={is_edit}
            >
              <option value={false}>{$LL.NO()}</option>
              <option value={true}>{$LL.YES()}</option>
            </select>
          </div>
        </div>
      {/if}
      <div class="option">
        <div>
          <label for="teams_allowed">{$LL.TOURNAMENTS.MANAGE.TEAMS_ALLOWED()}</label>
        </div>
        <div>
          <select name="teams_allowed" bind:value={data.teams_allowed} on:change={updateData} disabled={is_edit}>
            <option value={false}>{$LL.NO()}</option>
            <option value={true}>{$LL.YES()}</option>
          </select>
        </div>
      </div>
      {#if data.teams_allowed}
        <div class="indented">
          <div class="option">
            <div>
              <label for="teams_only">{$LL.TOURNAMENTS.MANAGE.TEAMS_ONLY()}</label>
            </div>
            <div>
              <select name="teams_only" bind:value={data.teams_only} on:change={updateData} disabled={is_edit}>
                <option value={false}>{$LL.NO()}</option>
                <option value={true}>{$LL.YES()}</option>
              </select>
            </div>
          </div>
          {#if data.teams_only}
            <div class="indented option">
              <div>
                <label for="team_members_only">{$LL.TOURNAMENTS.MANAGE.TEAM_MEMBERS_ONLY()}</label>
              </div>
              <div>
                <select name="team_members_only" bind:value={data.team_members_only} disabled={is_edit}>
                  <option value={false}>{$LL.NO()}</option>
                  <option value={true}>{$LL.YES()}</option>
                </select>
              </div>
            </div>
            <div class="indented option">
              <div>
                <label for="min_representatives">{$LL.TOURNAMENTS.MANAGE.MIN_REPRESENTATIVES()}</label>
              </div>
              <div>
                <input
                  class="number"
                  type="number"
                  name="min_representatives"
                  bind:value={data.min_representatives}
                  min="0"
                  max="3"
                  required
                />
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
  {#if !data.teams_allowed}
    <div class="option">
      <div>
        <label for="host_status_required">{$LL.TOURNAMENTS.MANAGE.HOST_STATUS_REQUIRED()}</label>
      </div>
      <div>
        <select name="host_status_required" bind:value={data.host_status_required} disabled={is_edit}>
          <option value={false}>{$LL.NO()}</option>
          <option value={true}>{$LL.YES()}</option>
        </select>
      </div>
    </div>
    <div class="option">
      <div>
        <label for="mii_name_required">{$LL.TOURNAMENTS.MANAGE.MII_NAME_REQUIRED()}</label>
      </div>
      <div>
        <select name="mii_name_required" bind:value={data.mii_name_required} disabled={is_edit}>
          <option value={false}>{$LL.NO()}</option>
          <option value={true}>{$LL.YES()}</option>
        </select>
      </div>
    </div>
    <div class="option">
      <div>
        <label for="require_single_fc"
          >{$LL.TOURNAMENTS.MANAGE.REQUIRE_SINGLE_FC()}</label
        >
      </div>
      <div>
        <select name="require_single_fc" bind:value={data.require_single_fc} disabled={is_edit}>
          <option value={false}>{$LL.NO()}</option>
          <option value={true}>{$LL.YES()}</option>
        </select>
      </div>
    </div>
    <div class="option">
      <div>
        <label for="checkins_enabled">{$LL.TOURNAMENTS.MANAGE.CHECKINS_ENABLED()}</label>
      </div>
      <div>
        <select name="checkins_enabled" bind:value={data.checkins_enabled} on:change={updateData}>
          <option value={false}>{$LL.NO()}</option>
          <option value={true}>{$LL.YES()}</option>
        </select>
      </div>
    </div>
    {#if data.checkins_enabled}
      <div class="option indented">
        <div>
          <label for="checkins_open">{$LL.TOURNAMENTS.MANAGE.CHECKINS_OPEN()}</label>
        </div>
        <div>
          <select name="checkins_open" bind:value={data.checkins_open} on:change={updateData}>
            <option value={false}>{$LL.NO()}</option>
            <option value={true}>{$LL.YES()}</option>
          </select>
        </div>
      </div>
      {#if data.is_squad}
        <div class="option indented">
          <div>
            <label for="min_players_checkin">{$LL.TOURNAMENTS.MANAGE.MIN_PLAYERS_CHECKIN()}</label>
          </div>
          <div>
            <input
              class="number"
              type="number"
              name="min_players_checkin"
              bind:value={data.min_players_checkin}
              min="1"
              max="99"
              required
            />
          </div>
        </div>
      {/if}
    {/if}
  {/if}
  <div class="option">
    <div>
      <label for="verification_required">{$LL.TOURNAMENTS.MANAGE.VERIFICATION_REQUIRED()}</label>
    </div>
    <div>
      <select name="verification_required" bind:value={data.verification_required}>
        <option value={false}>{$LL.NO()}</option>
        <option value={true}>{$LL.YES()}</option>
      </select>
    </div>
  </div>
</Section>
<Section header={$LL.TOURNAMENTS.MANAGE.TOURNAMENT_DESCRIPTION()}>
  {#if series}
    <div class="option">
      <div>
        <label for="use_series_description">{$LL.TOURNAMENTS.MANAGE.USE_SERIES_DESCRIPTION()}</label>
      </div>
      <div>
        <select name="use_series_description" bind:value={data.use_series_description} on:change={updateData}>
          <option value={false}>{$LL.NO()}</option>
          <option value={true}>{$LL.YES()}</option>
        </select>
      </div>
    </div>
  {/if}
  <div class="option">
    {#if series && data.use_series_description}
      <MarkdownTextArea name="description" value={series.description} disabled/>
    {:else}
      <MarkdownTextArea name="description" bind:value={data.description} on:change={updateData}/>
    {/if}
  </div>
</Section>
<Section header={$LL.TOURNAMENTS.MANAGE.TOURNAMENT_RULESET()}>
  {#if series}
    <div class="option">
      <div>
        <label for="use_series_ruleset">{$LL.TOURNAMENTS.MANAGE.USE_SERIES_RULESET()}</label>
      </div>
      <div>
        <select name="use_series_ruleset" bind:value={data.use_series_ruleset} on:change={updateData}>
          <option value={false}>{$LL.NO()}</option>
          <option value={true}>{$LL.YES()}</option>
        </select>
      </div>
    </div>
  {/if}
  <div class="option">
    {#if series && data.use_series_ruleset}
      <MarkdownTextArea name="ruleset" value={series.ruleset} disabled/>
    {:else}
      <MarkdownTextArea name="ruleset" bind:value={data.ruleset} on:change={updateData}/>
    {/if}
  </div>
</Section>
<Section header={$LL.TOURNAMENTS.MANAGE.TOURNAMENT_RULESET()}>
  <div class="option">
    <div>
      <label for="registrations_open">{$LL.TOURNAMENTS.MANAGE.REGISTRATIONS_OPEN()}</label>
    </div>
    <div>
      <select name="registrations_open" bind:value={data.registrations_open}>
        <option value={true}>{$LL.TOURNAMENTS.MANAGE.OPEN()}</option>
        <option value={false}>{$LL.TOURNAMENTS.MANAGE.CLOSED()}</option>
      </select>
    </div>
  </div>
  {#if !is_template}
    <div class="option">
      <div>
        <label for="registration_deadline">{$LL.TOURNAMENTS.MANAGE.REGISTRATION_DEADLINE()}</label>
      </div>
      <div>
        <input
          name="registration_deadline"
          type="datetime-local"
          value={getDateTimeLocal(data.registration_deadline)}
        />
      </div>
    </div>
  {/if}
  <div class="option">
    <div>
      <label for="registration_cap">{$LL.TOURNAMENTS.MANAGE.REGISTRATION_CAP()}</label>
    </div>
    <div>
      <input name="registration_cap" type="number" min="0" bind:value={data.registration_cap} />
    </div>
  </div>
</Section>
<Section header={$LL.TOURNAMENTS.MANAGE.TOURNAMENT_STATUS()}>
  <div class="option">
    <div>
      <label for="is_viewable">{$LL.TOURNAMENTS.MANAGE.IS_VIEWABLE()}</label>
    </div>
    <div>
      <select name="is_viewable" bind:value={data.is_viewable} on:change={updateData}>
        <option value={true}>{$LL.YES()}</option>
        <option value={false}>{$LL.NO()}</option>
      </select>
    </div>
  </div>
  {#if data.is_viewable}
    <div class="option indented">
      <div>
        <label for="is_public">{$LL.TOURNAMENTS.MANAGE.IS_PUBLIC()}</label>
      </div>
      <div>
        <select name="is_public" bind:value={data.is_public}>
          <option value={true}>{$LL.SHOW()}</option>
          <option value={false}>{$LL.HIDE()}</option>
        </select>
      </div>
    </div>
  {/if}
  <div class="option">
    <div>
      <label for="show_on_profiles">{$LL.TOURNAMENTS.MANAGE.SHOW_ON_PROFILES()}</label>
    </div>
    <div>
      <select name="show_on_profiles" bind:value={data.show_on_profiles}>
        <option value={true}>{$LL.SHOW()}</option>
        <option value={false}>{$LL.HIDE()}</option>
      </select>
    </div>
  </div>
  {#if series}
    <div class="option">
      <div>
        <label for="series_stats_include">{$LL.TOURNAMENTS.MANAGE.SERIES_STATS_INCLUDE()}</label>
      </div>
      <div>
        <select name="series_stats_include" bind:value={data.series_stats_include}>
          <option value={true}>{$LL.YES()}</option>
          <option value={false}>{$LL.NO()}</option>
        </select>
      </div>
    </div>
  {/if}
</Section>

<style>
  div.option {
    margin-bottom: 10px;
  }
  div.indented {
    padding-left: 1em;
  }
  input.tournament_name {
    width: 90%;
  }
</style>
