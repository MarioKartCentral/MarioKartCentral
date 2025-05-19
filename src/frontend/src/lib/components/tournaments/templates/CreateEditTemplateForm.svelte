<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { CreateTemplate } from '$lib/types/tournaments/templates/create-template';
  import TournamentDetailsForm from '../TournamentDetailsForm.svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import type { TournamentTemplate } from '$lib/types/tournaments/create/tournament-template';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  export let template_id: number | null = null;
  export let is_edit = false;
  export let series_restrict = false;
  export let series_id: number | null = null;

  let template: TournamentTemplate | null = null;

  let data: CreateTemplate = {
    template_name: '',
    name: '',
    series_id: null,
    date_start: 0,
    date_end: 0,
    logo: null,
    use_series_logo: false,
    url: null,
    organizer: 'MKCentral',
    location: null,
    game: 'mkworld',
    mode: '150cc',
    is_squad: false,
    min_squad_size: null,
    max_squad_size: null,
    squad_tag_required: false,
    squad_name_required: false,
    teams_allowed: false,
    teams_only: false,
    team_members_only: false,
    min_representatives: null,
    host_status_required: false,
    mii_name_required: false,
    require_single_fc: false,
    checkins_enabled: false,
    checkins_open: false,
    min_players_checkin: null,
    verification_required: false,
    use_series_description: false,
    description: '',
    use_series_ruleset: false,
    ruleset: '',
    registrations_open: false,
    registration_cap: null,
    registration_deadline: null,
    is_viewable: true,
    is_public: true,
    is_deleted: false,
    show_on_profiles: true,
    series_stats_include: false,
    verified_fc_required: false,
    bagger_clause_enabled: false,
    logo_file: null,
    remove_logo: false,
  };

  function updateData() {
    data = data;
  }

  let data_retrieved = false;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    data.series_id = series_id;
    if (!template_id) {
      data_retrieved = true;
      return;
    }
    const res = await fetch(`/api/tournaments/templates/${template_id}`);
    if (res.status === 200) {
      const body: TournamentTemplate = await res.json();
      template = body;
      data = Object.assign(data, template);
    }
    data_retrieved = true;
  });

  async function createTemplate() {
    let payload = data;
    console.log(payload);
    const endpoint = '/api/tournaments/templates/create';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      goto(`/${$page.params.lang}/tournaments/templates`);
      alert($LL.TOURNAMENTS.TEMPLATES.CREATE_TEMPLATE_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.TEMPLATES.CREATE_TEMPLATE_FAILED()}: ${result['title']}`);
    }
  }

  async function editTemplate() {
    let payload = data;
    console.log(payload);
    const endpoint = `/api/tournaments/templates/${template_id}/edit`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      goto(`/${$page.params.lang}/tournaments/templates`);
      alert($LL.TOURNAMENTS.TEMPLATES.EDIT_TEMPLATE_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.TEMPLATES.EDIT_TEMPLATE_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if data_retrieved}
  {#if check_series_permission(user_info,
    is_edit ? series_permissions.edit_tournament_template : series_permissions.create_tournament_template,
    data.series_id
  )}
    <form method="POST" on:submit|preventDefault={is_edit ? editTemplate : createTemplate}>
      <Section header={$LL.TOURNAMENTS.TEMPLATES.TEMPLATE_DETAILS()}>
        <div>
          <label for="template_name">{$LL.TOURNAMENTS.TEMPLATES.TEMPLATE_NAME()}</label>
        </div>
        <div>
          <input type="text" bind:value={data.template_name} required />
        </div>
      </Section>
      <TournamentDetailsForm {data} update_function={updateData} is_template={true} {series_restrict} />
      <Section header={$LL.COMMON.SUBMIT()}>
        <Button type="submit">
          {is_edit ? $LL.TOURNAMENTS.TEMPLATES.EDIT_TEMPLATE() : $LL.TOURNAMENTS.TEMPLATES.CREATE_TEMPLATE()}
        </Button>
      </Section>
    </form>
  {/if}
{/if}
