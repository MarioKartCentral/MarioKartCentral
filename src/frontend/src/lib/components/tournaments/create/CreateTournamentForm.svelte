<script lang="ts">
    import { onMount } from "svelte";
    import type { TournamentTemplate } from "$lib/types/tournaments/create/tournament-template";
    import Section from "$lib/components/common/Section.svelte";
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import type { CreateTournament } from "$lib/types/tournaments/create/create-tournament";
    import TournamentDetailsForm from "../TournamentDetailsForm.svelte";

    export let template_id: number | null = null;
    let template: TournamentTemplate | null = null;

    let data: CreateTournament = {
        tournament_name: "",
        series_id: null,
        date_start: null,
        date_end: null,
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

    async function createTournament(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        function getDate(name: string) {
            let date_form = formData.get(name);
            if(!date_form) {
                return null;
            }
            let date = new Date(date_form.toString());
            return date.getTime() / 1000; //return date in seconds
        }

        let date_start: number | null = getDate("date_start");
        let date_end: number | null = getDate("date_end");
        let registration_deadline: number | null = getDate("registration_deadline");
        if(date_start && date_end && date_start > date_end) {
            alert("Starting date must be after ending date");
            return;
        }
        data.date_start = date_start;
        data.date_end = date_end;
        data.registration_deadline = registration_deadline;
        
        let payload = data;
        console.log(payload);
        const endpoint = '/api/tournaments/create';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            goto(`/${$page.params.lang}/tournaments`);
            alert('Successfully created tournament!');
        } else {
            alert(`Creating tournament failed: ${result['title']}`);
        }
    }
</script>

<form method="POST" on:submit|preventDefault={createTournament}>
    <TournamentDetailsForm data={data} update_function={updateData}/>
    <Section header="Submit">
        <button type="submit">Create Tournament</button>
    </Section>
</form>