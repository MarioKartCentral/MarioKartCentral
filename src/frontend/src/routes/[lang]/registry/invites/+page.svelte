<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { PlayerInvites } from "$lib/types/player-invites";
    import { onMount } from 'svelte';

    let invites: PlayerInvites;

    onMount(async () => {
        const res = await fetch(`/api/user/me/invites`);
        if (res.status != 200) {
            return;
        }
        const body: PlayerInvites = await res.json();
        invites = body;
    });
</script>

{#if invites}
    <Section header="Team Invites">
        {#each invites.team_invites as invite}
            {invite.team_name}
        {/each}
    </Section>

    <Section header="Tournament Invites">

    </Section>
{/if}
