<script lang="ts">
  export let country_code: string | null;
</script>

<span>
  <img src={'/src/lib/assets/flags/' + country_code?.toUpperCase() + '.png'} alt={country_code} class="flag" />
</span>

<style>
  img.flag {
    max-height: 36px;
    display: inline;
  }
</style>
