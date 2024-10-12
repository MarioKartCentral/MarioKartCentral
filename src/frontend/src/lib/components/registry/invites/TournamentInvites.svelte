<script lang="ts">
    import Table from "$lib/components/common/Table.svelte";
    import { page } from "$app/stores";
    import TagBadge from "$lib/components/badges/TagBadge.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { locale } from "$i18n/i18n-svelte";
    import ArrowRight from "$lib/components/common/ArrowRight.svelte";
    import type { TournamentInvite } from "$lib/types/tournament-invite";
    import BaggerBadge from "$lib/components/badges/BaggerBadge.svelte";

    export let invites: TournamentInvite[];

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };
</script>

{#if invites.length}
    <Table>
        <col class="tournament"/>
        <col class="squad"/>
        <col class="date mobile-hide"/>
        <col class="button"/>
        <thead>
            <tr>
                <th>Tournament</th>
                <th>Squad</th>
                <th class="mobile-hide">Date</th>
                <th>Accept/Deny</th>
            </tr>
        </thead>
        <tbody>
            {#each invites as invite, i}
                <tr class="row-{i % 2}">
                    <td>
                        <a href="/{$page.params.lang}/tournaments/details?id={invite.tournament_id}">
                            {invite.tournament_name}
                            {#if invite.is_bagger_clause}
                                <BaggerBadge/>
                            {/if}
                        </a>
                    </td>
                    <td>
                        {#if invite.squad_tag}
                            <span class="tag">
                                <TagBadge tag={invite.squad_tag} color={invite.squad_color}/>
                            </span>
                            
                        {/if}
                        {#if invite.squad_name}
                            {invite.squad_name}
                        {/if}
                    </td>
                    <td class="mobile-hide">
                        {new Date(invite.timestamp * 1000).toLocaleString($locale, options)}
                    </td>
                    <td>
                        <Button href="/{$page.params.lang}/tournaments/details?id={invite.tournament_id}">
                            Tournament Page
                            <ArrowRight/>
                        </Button>
                    </td>
                </tr>
            {/each}
        </tbody>
    </Table>
{:else}
    No invites.
{/if}

<style>
    span.tag {
        margin-right: 5px;
    }
    col.tournament {
        width: 30%;
    }
    col.squad {
        width: 20%;
    }
    col.date {
        width: 20%;
    }
    col.button {
        width: 30%;
    }
</style>