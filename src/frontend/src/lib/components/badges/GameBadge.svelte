<script lang="ts">
  import Badge from "./Badge.svelte";

  export let game: string;
</script>

<Badge badgeClass={'game_' + game + '_badge wide'}>{game.toUpperCase()}</Badge>

<style>
  :global(.game_mkt_badge) {
    background-color: #a1385d;
    border: 1px solid #8e1643;
  }

  :global(.game_smk_badge) {
    background-color: #52a3a3;
    border: 1px solid #247373;
  }

  :global(.game_mkw_badge) {
    background-color: #65bedc;
    border: 1px solid #57a2c8;
  }

  :global(.game_mk7_badge) {
    background-color: #ab5555;
    border: 1px solid #902a2a;
  }

  :global(.game_mk8_badge) {
    background-color: #5555ab;
    border: 1px solid #282887;
  }

  :global(.game_mk8dx_badge) {
    background-color: #9755ab;
    border: 1px solid #892bad;
  }
</style>
