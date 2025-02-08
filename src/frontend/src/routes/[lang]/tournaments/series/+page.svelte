<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { TournamentSeriesBasic } from '$lib/types/tournaments/series/tournament-series';
  import { check_permission, permissions } from '$lib/util/permissions';
  import { onMount } from 'svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import SeriesPageItem from '$lib/components/tournaments/series/SeriesPageItem.svelte';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let series: TournamentSeriesBasic[] = [];

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

<Section header={$LL.TOURNAMENTS.TOURNAMENT_SERIES()}>
  <div slot="header_content">
    {#if check_permission(user_info, permissions.create_series)}
      <Button href="/{$page.params.lang}/tournaments/series/create">{$LL.TOURNAMENTS.SERIES.CREATE()}</Button>
    {/if}
  </div>
</Section>

{#each series as s}
  <SeriesPageItem series={s} />
{/each}
