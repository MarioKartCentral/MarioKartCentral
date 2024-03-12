<script lang="ts">
  export let recruiting: string;
  const recruitingStr = recruiting == '1' ? 'Recruiting' :  'Not Recruiting'
  const recruitingId = recruiting == '1' ? 'recruiting' :  'not_recruiting'
</script>

<div>
  <span class={recruitingId + '_badge'}>{recruitingStr}</span>
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

  .recruiting_badge {
    background-color: #00997b;
    border: 1px solid #006b5c;
  }

  .not_recruiting_badge {
    background-color: #7f7f80;
    border: 1px solid #4b4b4b;
  }
</style>
