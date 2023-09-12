<script lang="ts">
  import { onMount, getContext } from 'svelte';
  import TournamentPageItem from '$lib/components/tournaments/TournamentPageItem.svelte';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import Section from '$lib/components/common/Section.svelte';
  import { addPermission, permissions } from '$lib/util/util';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';

  addPermission(permissions.create_tournament);

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let tournaments: TournamentListItem[] = [];
  

  onMount(async () => {
    const res = await fetch('/api/tournaments/list');
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        tournaments.push(t);
      }
      tournaments = tournaments;
    }
  });
</script>

<Section header="Tournaments">
  <div slot="header_content">
    {#if user_info.permissions.includes(permissions.create_tournament)}
    Create Tournament
    {/if}
    
  </div>
  {#each tournaments as tournament}
    <TournamentPageItem {tournament} />
  {/each}
</Section>
