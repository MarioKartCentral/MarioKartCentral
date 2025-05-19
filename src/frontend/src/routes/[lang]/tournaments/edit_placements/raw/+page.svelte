<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import type { TournamentPlacementList, TournamentPlacementSimple } from "$lib/types/tournament-placement";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import LL from "$i18n/i18n-svelte";

    let id = 0;
    let is_loaded = false;
    let placements: TournamentPlacementList;

    let text = "";

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);

        const res = await fetch(`/api/tournaments/${id}/placements`);
        let placements_body: TournamentPlacementList = await res.json();
        placements = placements_body;
        for(let placement of placements.placements) {
            // if it's a solo tournament, we want to use player ID instead of registration ID
            // since you can't view tournament player IDs on frontend
            let curr_line = `${placement.registration_id}\t\t`
            if(placement.placement_lower_bound) {
                curr_line += `${placement.placement}-${placement.placement_lower_bound}`;
            }
            else if(placement.is_disqualified) {
                curr_line += `DQ`;
            }
            else {
                curr_line += `${placement.placement}`;
            }
            if(placement.placement_description) {
                curr_line += `\t${placement.placement_description}`;
            }
            curr_line += "\n";
            text += curr_line;
        }
        is_loaded = true;
    });

    async function savePlacements() {
        let new_placements: TournamentPlacementSimple[] = [];
        let lines = text.split("\n");
        for(let line of lines) {
            let vals = line.split(/[ \t]+/);
            if(vals.length < 2) {
                continue;
            }
            try {
                let reg_id = Number(vals[0]);
                if(isNaN(reg_id)) {
                    alert($LL.TOURNAMENTS.PLACEMENTS.PLACEMENT_LINE_INCORRECT({line: line}));
                    return;
                }
                let placement: number | null;
                let is_disqualified = false;
                let lower_bound: number | null = null;
                let description: string | null = null;
                if(vals[1].toUpperCase() === "DQ") {
                    placement = null;
                    is_disqualified = true;
                }
                else {
                    let range = vals[1].split("-");
                    for(let n in range) {
                        if(isNaN(Number(n))) {
                            alert($LL.TOURNAMENTS.PLACEMENTS.PLACEMENT_LINE_INCORRECT({line: line}));
                            return;
                        }
                    }
                    if(range.length > 1) {
                        lower_bound = Number(range[1]);
                    }
                    placement = Number(range[0]);
                }
                if(vals.length > 2) {
                    description = vals.splice(2).join(" ");
                }
                new_placements.push({registration_id: reg_id, placement: placement, is_disqualified: is_disqualified, 
                    placement_lower_bound: lower_bound, placement_description: description});
            }
            catch(e) {
                alert(`${$LL.TOURNAMENTS.PLACEMENTS.PARSE_TEXT_ERROR()}: ${e}`);
            }
        }

        const endpoint = `/api/tournaments/${id}/placements/set`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(new_placements),
        });
        console.log(new_placements);
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.TOURNAMENTS.PLACEMENTS.SAVE_PLACEMENTS_FAILED()}: ${result['title']}`);
        }

    }
</script>

{#if is_loaded}
    <Section header={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>
        <div slot="header_content">
            <Button href="/{$page.params.lang}/tournaments/details?id={id}">{$LL.COMMON.BACK()}</Button>
        </div>
    </Section>
    <Section header={$LL.TOURNAMENTS.PLACEMENTS.EDIT_PLACEMENTS()}>
        <div slot="header_content">
            <Button href="/{$page.params.lang}/tournaments/edit_placements?id={id}">{$LL.TOURNAMENTS.PLACEMENTS.SWITCH_TO_INTERACTIVE_INPUT()}</Button>
            <Button href="/{$page.params.lang}/tournaments/edit_placements/raw_player_id?id={id}">{$LL.TOURNAMENTS.PLACEMENTS.RAW_INPUT_PLAYER_ID()}</Button>
        </div>
        <div>
            {$LL.TOURNAMENTS.PLACEMENTS.RAW_INPUT_INSTRUCTIONS()}
        </div>
        <div>
            <textarea bind:value={text}/>
        </div>
        <div>
            <Button on:click={savePlacements}>{$LL.COMMON.SAVE()}</Button>
        </div>
    </Section>
{/if}

<style>
    textarea {
        width: 90%;
        height: 500px;
        tab-size: 4;
    }
</style>