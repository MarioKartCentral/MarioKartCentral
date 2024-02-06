<script lang="ts">
  export let value:string;
  export let type:string;
</script>

<div>
  <span class={type + "_" + value.toLowerCase() + '_badge'}>{value}</span>
</div>

<style>
  .game_mkt_badge {
    display: inline-block;
    text-align: center;
    background-color: #a1385d;
    color: white;
    border: 1px solid #8e1643;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .game_smk_badge {
    display: inline-block;
    text-align: center;
    background-color: #52a3a3;
    color: white;
    border: 1px solid #247373;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .game_mkw_badge {
    display: inline-block;
    text-align: center;
    background-color: #65bedc;
    color: white;
    border: 1px solid #57a2c8;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .game_mk7_badge {
    display: inline-block;
    text-align: center;
    background-color: #ab5555;
    color: white;
    border: 1px solid #902a2a;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .game_mk8u_badge {
    display: inline-block;
    text-align: center;
    background-color: #5555ab;
    color: white;
    border: 1px solid #282887;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .game_mk8dx_badge {
    display: inline-block;
    text-align: center;
    background-color: #9755ab;
    color: white;
    border: 1px solid #892bad;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .mode_vsrace_badge,
  .mode_150cc_badge {
    display: inline-block;
    text-align: center;
    background-color: #008fd4;
    color: white;
    border: 1px solid #005ea8;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .mode_200cc_badge {
    display: inline-block;
    text-align: center;
    background-color: #d4008b;
    color: white;
    border: 1px solid #990063;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .mode_mixed_battle_badge,
  .mode_balloon_ballon_badge,
  .mode_shine_thief_badge,
  .mode_bobomb_blast_badge,
  .mode_coin_runners_badge,
  .mode_renegade_roundup_badge {
    display: inline-block;
    text-align: center;
    background-color: #00994d;
    color: white;
    border: 1px solid #006631;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .mode_mixed_badge {
    display: inline-block;
    text-align: center;
    background-color: #7600a1;
    color: white;
    border: 1px solid #5b0080;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .mode_match_race_badge {
    display: inline-block;
    text-align: center;
    background-color: #009fa1;
    color: white;
    border: 1px solid #006e6e;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .type_team_badge {
    display: inline-block;
    text-align: center;
    background-color: #006ea1;
    color: white;
    border: 1px solid #004c80;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .type_solo_badge {
    display: inline-block;
    text-align: center;
    background-color: #a1006b;
    color: white;
    border: 1px solid #6b0040;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }

  .type_squad_badge {
    display: inline-block;
    text-align: center;
    background-color: #006633;
    color: white;
    border: 1px solid #005621;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px;
    width: 100px;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
      sans-serif;
    font-size: 78%;
  }
</style>
