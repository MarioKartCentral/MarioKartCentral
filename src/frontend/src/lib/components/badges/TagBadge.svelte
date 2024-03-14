<script lang="ts">
  import type { Team } from '$lib/types/team';
  import { colors, team_permissions } from '$lib/util/util';
  import Badge from './Badge.svelte';

  export let tag: string | null;
  export let color: number;

  let color_val = colors[color % colors.length].value;

  // $: if (team.color > 0 && team.color < 41) {
  //   color = colors[team.color - 1].value;
  // }
</script>

<Badge badgeClass="tag_badge" style="background-color:{color_val};border: 1px solid {color_val}">
  {tag ? tag : "-"}
</Badge>
<!-- 
<span class={'tag_badge'} style:background-color={color_val}>
  {team.tag}
</span> -->

<style>
  :global(.tag_badge) {
    width: 60px;
    font-weight: 700;
  }
</style>
