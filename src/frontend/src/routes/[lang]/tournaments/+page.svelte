<script lang="ts">
  import { onMount } from 'svelte';
  import TournamentPageItem from '$lib/components/tournaments/TournamentPageItem.svelte';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import Section from '$lib/components/common/Section.svelte';
  import { addPermission, permissions } from '$lib/util/util';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import LinkButton from '$lib/components/common/LinkButton.svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';

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

<a href="/{$page.params.lang}/tournaments/series">Series</a>
<a href="/{$page.params.lang}/tournaments/templates">Templates</a>

<Section header={$LL.NAVBAR.TOURNAMENTS()}>
  <div slot="header_content">
    {#if user_info.permissions.includes(permissions.create_tournament)}
      <LinkButton href="/{$page.params.lang}/tournaments/create/select_template">Create Tournament</LinkButton>
    {/if}
  </div>
  {#each tournaments as tournament}
    <TournamentPageItem {tournament} />
  {/each}
</Section>
