<script lang="ts">
  export let game: string;
</script>

<div>
  <span class={'game_' + game + '_badge'}>{game.toUpperCase()}</span>
</div>

<style>
  span {
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

  .game_mkt_badge {
    background-color: #a1385d;
    border: 1px solid #8e1643;
  }

  .game_smk_badge {
    background-color: #52a3a3;
    border: 1px solid #247373;
  }

  .game_mkw_badge {
    background-color: #65bedc;
    border: 1px solid #57a2c8;
  }

  .game_mk7_badge {
    background-color: #ab5555;
    border: 1px solid #902a2a;
  }

  .game_mk8u_badge {
    background-color: #5555ab;
    border: 1px solid #282887;
  }

  .game_mk8dx_badge {
    background-color: #9755ab;
    border: 1px solid #892bad;
  }
</style>
