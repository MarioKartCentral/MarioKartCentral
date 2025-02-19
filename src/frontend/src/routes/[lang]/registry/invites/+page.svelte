<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { PlayerInvites } from '$lib/types/player-invites';
  import { onMount } from 'svelte';
  import TournamentInvites from '$lib/components/registry/invites/TournamentInvites.svelte';
  import TeamInvites from '$lib/components/registry/invites/TeamInvites.svelte';
  import LL from '$i18n/i18n-svelte';

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
  <Section header={$LL.INVITES.TEAM_INVITES()}>
    <TeamInvites invites={invites.team_invites}/>
  </Section>

  <Section header={$LL.INVITES.TOURNAMENT_INVITES()}>
    <TournamentInvites invites={invites.tournament_invites}/>
  </Section>
{/if}