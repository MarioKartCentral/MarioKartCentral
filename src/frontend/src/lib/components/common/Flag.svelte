<script lang="ts">
  export let country_code: string | null;
</script>

<img src={'/src/lib/assets/flags/' + country_code?.toUpperCase() + '.png'} alt={country_code} class="flag" />

<style>
  img.flag {
    height: 36px;
  }
</style>
