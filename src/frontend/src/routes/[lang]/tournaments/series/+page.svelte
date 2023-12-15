<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import { addPermission, permissions } from '$lib/util/util';
  import { onMount } from 'svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import LinkButton from '$lib/components/common/LinkButton.svelte';
  import { page } from '$app/stores';
  import SeriesPageItem from '$lib/components/tournaments/series/SeriesPageItem.svelte';

  addPermission(permissions.create_series);

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let series: TournamentSeries[] = [];

  onMount(async () => {
    const res = await fetch('/api/tournaments/series/list');
    if (res.status === 200) {
      const body = await res.json();
      for (let s of body) {
        series.push(s);
      }
      series.sort((a, b) => a.display_order - b.display_order);
      series = series;
    }
  });
</script>

<Section header="Tournament Series">
  <div slot="header_content">
    {#if user_info.permissions.includes(permissions.create_series)}
      <LinkButton href="/{$page.params.lang}/tournaments/series/create">Create Series</LinkButton>
    {/if}
  </div>
</Section>

{#each series as s}
  <SeriesPageItem series={s} />
{/each}
