<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { PlayerInvites } from '$lib/types/player-invites';
  import { onMount } from 'svelte';
  import TournamentInvites from '$lib/components/registry/invites/TournamentInvites.svelte';
  import TeamInvites from '$lib/components/registry/invites/TeamInvites.svelte';

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
    <TeamInvites invites={invites.team_invites}/>
  </Section>

  <Section header="Tournament Invites">
    <TournamentInvites invites={invites.tournament_invites}/>
  </Section>
{/if}