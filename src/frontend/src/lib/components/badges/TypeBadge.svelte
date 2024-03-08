<script lang="ts">
  export let type: string;
</script>

<div>
  <span class={'type_' + type.toLowerCase() + '_badge'}>{type}</span>
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

  .type_team_badge {
    background-color: #006ea1;
    border: 1px solid #004c80;
  }

  .type_solo_badge {
    background-color: #a1006b;
    border: 1px solid #6b0040;
  }

  .type_squad_badge {
    background-color: #006633;
    border: 1px solid #005621;
  }
</style>
