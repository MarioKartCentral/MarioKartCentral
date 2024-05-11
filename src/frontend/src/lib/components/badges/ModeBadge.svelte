<script lang="ts">
  import Badge from "./Badge.svelte";
  import { mode_names } from "$lib/util/util";

  export let mode: string;
</script>

<Badge badgeClass={'mode_' + mode.toLowerCase() + '_badge wide'}>{mode_names[mode]}</Badge>

<style>
  :global(.mode_mixed_badge,
  .mode_mixed_battle_badge,
  .mode_balloon_ballon_badge,
  .mode_shine_thief_badge,
  .mode_bobomb_blast_badge,
  .mode_coin_runners_badge,
  .mode_renegade_roundup_badge) {
    background-color: #00994d;
    border: 1px solid #006631;
  }

  :global(.mode_vsrace_badge,
  .mode_150cc_badge,
  .mode_rt_badge) {
    background-color: #008fd4;
    border: 1px solid #005ea8;
  }

  :global(
    .mode_200cc_badge,
    .mode_ct_badge
  ) {
    background-color: #d4008b;
    border: 1px solid #990063;
  }

  :global(.mode_match_race_badge) {
    background-color: #009fa1;
    border: 1px solid #006e6e;
  }

  :global(.mode_mixed_badge) {
    background-color: #7600a1;
    border: 1px solid #5b0080;
  }
</style>
