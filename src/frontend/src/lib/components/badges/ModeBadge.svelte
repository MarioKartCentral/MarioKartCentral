<script lang="ts">
  export let mode: string;
</script>

<div>
  <span class={'mode_' + mode.toLowerCase() + '_badge'}>{mode}</span>
</div>

<style>
  .mode_vsrace_badge,
  .mode_150cc_badge,
  .mode_200cc_badge,
  .mode_match_race_badge,
  .mode_mixed_badge,
  .mode_mixed_battle_badge,
  .mode_balloon_ballon_badge,
  .mode_shine_thief_badge,
  .mode_bobomb_blast_badge,
  .mode_coin_runners_badge,
  .mode_renegade_roundup_badge {
    display: inline-block;
    text-align: center;
    color: white;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .mode_mixed_badge,
  .mode_mixed_battle_badge,
  .mode_balloon_ballon_badge,
  .mode_shine_thief_badge,
  .mode_bobomb_blast_badge,
  .mode_coin_runners_badge,
  .mode_renegade_roundup_badge {
    background-color: #00994d;
    border: 1px solid #006631;
  }

  .mode_vsrace_badge,
  .mode_150cc_badge {
    background-color: #008fd4;
    border: 1px solid #005ea8;
  }

  .mode_200cc_badge {
    background-color: #d4008b;
    border: 1px solid #990063;
  }

  .mode_match_race_badge {
    background-color: #009fa1;
    border: 1px solid #006e6e;
  }

  .mode_mixed_badge {
    background-color: #7600a1;
    border: 1px solid #5b0080;
  }
</style>
