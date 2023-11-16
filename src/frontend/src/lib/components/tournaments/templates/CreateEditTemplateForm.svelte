<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { CreateTemplate } from "$lib/types/tournaments/templates/create-template";
    import TournamentDetailsForm from "../TournamentDetailsForm.svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import type { TournamentTemplate } from "$lib/types/tournaments/create/tournament-template";

    export let template_id: number | null = null;
    export let is_edit: boolean = false;

    let template: TournamentTemplate | null = null;

    let data: CreateTemplate = {
        template_name: "",
        tournament_name: "",
        series_id: null,
        date_start: 0,
        date_end: 0,
        logo: null,
        use_series_logo: false,
        url: null,
        organizer: "MKCentral",
        location: null,
        game: "mk8dx",
        mode: "150cc",
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
        checkins_open: false,
        min_players_checkin: null,
        verification_required: false,
        use_series_description: false,
        description: "",
        use_series_ruleset: false,
        ruleset: "",
        registrations_open: false,
        registration_cap: null,
        registration_deadline: null,
        is_viewable: true,
        is_public: true,
        show_on_profiles: true,
        series_stats_include: false,
        verified_fc_required: false,
    };

    function updateData() {
        data = data;
    }

    onMount(async() => {
        if(!template_id) {
            return;
        }
        const res = await fetch(`/api/tournaments/templates/${template_id}`);
        if(res.status === 200) {
            const body: TournamentTemplate = await res.json();
            template = body;
            data = Object.assign(data, template);
        }
    });

    async function createTemplate(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
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
            alert('Successfully created template!');
        } else {
            alert(`Creating template failed: ${result['title']}`);
        }
    }

    async function editTemplate(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
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
            alert('Successfully edited template!');
        } else {
            alert(`Editing template failed: ${result['title']}`);
        }
    }
</script>

<form method="POST" on:submit|preventDefault={is_edit ? editTemplate : createTemplate}>
    <Section header="Template Details">
        <div>
            <label for="template_name">Template Name</label>
        </div>
        <div>
            <input type="text" bind:value={data.template_name} required/>
        </div>
    </Section>
    <TournamentDetailsForm data={data} update_function={updateData} is_template={true}/>
    <Section header="Submit">
        <button type="submit">
            {is_edit ? "Edit Template" : "Create Template"}
        </button>
    </Section>
</form>
