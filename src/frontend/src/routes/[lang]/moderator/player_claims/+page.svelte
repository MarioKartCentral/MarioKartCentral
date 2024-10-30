<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { onMount } from "svelte";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import { check_permission, permissions } from "$lib/util/permissions";
    import type { PlayerClaim } from "$lib/types/player-claim";
    import Table from "$lib/components/common/Table.svelte";
    import { page } from "$app/stores";
    import Flag from "$lib/components/common/Flag.svelte";
    import ConfirmButton from "$lib/components/common/buttons/ConfirmButton.svelte";
    import CancelButton from "$lib/components/common/buttons/CancelButton.svelte";
    import { locale } from "$i18n/i18n-svelte";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let claims: PlayerClaim[] = [];

    onMount(async() => {
        const res = await fetch('/api/registry/players/claims');
        if(res.status !== 200) {
            return;
        }
        const body: PlayerClaim[] = await res.json();
        claims = body.filter((c) => c.approval_status === "pending");
    });

    async function approveClaim(claim: PlayerClaim) {
        const payload = {
            claim_id: claim.id
        };
        const endpoint = "/api/registry/players/approveClaim"
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        }
        else {
            alert(`Approving player claim failed: ${result['title']}`);
        }
    }

    async function denyClaim(claim: PlayerClaim) {
        const payload = {
            claim_id: claim.id
        };
        const endpoint = "/api/registry/players/denyClaim"
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        }
        else {
            alert(`Denying player claim failed: ${result['title']}`);
        }
    }

    const options: Intl.DateTimeFormatOptions = {
        dateStyle: 'short',
        timeStyle: 'short',
    };
</script>

{#if check_permission(user_info, permissions.manage_shadow_players)}
    <Section header="Unapproved Player Claims">
        {#if claims.length}
            <Table>
                <col class="country"/>
                <col class="player"/>
                <col class="country"/>
                <col class="claimed"/>
                <col class="date mobile-hide"/>
                <col class="approve"/>
                <thead>
                    <tr>
                        <th/>
                        <th>Player</th>
                        <th/>
                        <th>Claimed Player</th>
                        <th class="mobile-hide">Date</th>
                        <th>Approve?</th>
                    </tr>
                </thead>
                <tbody>
                    {#each claims as claim, i}
                        <tr class="row-{i % 2}">
                            <td><Flag country_code={claim.player.country_code}/></td>
                            <td>
                                <a href="{$page.params.lang}/registry/players/profile?id={claim.player.id}">
                                    {claim.player.name}
                                </a>
                            </td>
                            <td><Flag country_code={claim.claimed_player.country_code}/></td>
                            <td>
                                <a href="{$page.params.lang}/registry/players/profile?id={claim.claimed_player.id}">
                                    {claim.claimed_player.name}
                                </a>
                            </td>
                            <td class="mobile-hide">
                                {new Date(claim.date * 1000).toLocaleString($locale, options)}
                            </td>
                            <td>
                                <ConfirmButton on:click={() => approveClaim(claim)}/>
                                <CancelButton on:click={() => denyClaim(claim)}/>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </Table>
        {:else}
            No player claims.
        {/if}
    </Section>
{:else}
    You do not have permission to access this page.
{/if}

<style>
    col.country {
        width: 5%;
    }
</style>