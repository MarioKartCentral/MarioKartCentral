<script lang="ts">
  import { onMount } from 'svelte';
  import TournamentPageItem from '$lib/components/tournaments/TournamentPageItem.svelte';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import Section from '$lib/components/common/Section.svelte';
  //import { addPermission, permissions } from '$lib/util/util';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, series_permissions } from '$lib/util/permissions';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';

  //addPermission(permissions.create_tournament);

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

<Section header={$LL.NAVBAR.TOURNAMENTS()}>
  <div slot="header_content">
    {#if check_permission(user_info, series_permissions.create_tournament)}
      <Button href="/{$page.params.lang}/tournaments/create/select_template">Create Tournament</Button>
    {/if}
  </div>
  {#each tournaments as tournament}
    <TournamentPageItem {tournament} />
  {/each}
</Section>
