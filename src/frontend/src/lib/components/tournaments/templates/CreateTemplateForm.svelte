<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { CreateTemplate } from "$lib/types/tournaments/templates/create-template";
    import TournamentDetailsForm from "../TournamentDetailsForm.svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";

    let data: CreateTemplate = {
        template_name: "",
        tournament_name: "",
        series_id: null,
        date_start: 0,
        date_end: 0,
        logo: null,
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

    async function createTemplate(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if(!data.series_id) {
            data.use_series_description = false;
            data.use_series_ruleset = false;
            data.series_stats_include = false;
        }
        
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
</script>

<form method="POST" on:submit|preventDefault={createTemplate}>
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
        <button type="submit">Create Template</button>
    </Section>
</form>
