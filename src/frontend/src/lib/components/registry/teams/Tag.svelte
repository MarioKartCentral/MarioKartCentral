<script lang="ts">
  import type { Team } from '$lib/types/team';
  export let team: Team;
  import { colors } from '$lib/util/util';

  let color = '#808080';

  $: if (team.color > 0 && team.color < 41) {
    color = colors[team.color - 1].value;
  }
</script>

<span class={'tag_badge'} style:background-color={color}>
  {team.tag}
</span>

<style>
  .tag_badge {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border-radius: 6px;
    display: inline-block;
    text-align: center;
    width: 40px;
    vertical-align: middle;
    overflow: hidden;
    height: 30px;
    line-height: 30px;
    position: relative;
  }
</style>
