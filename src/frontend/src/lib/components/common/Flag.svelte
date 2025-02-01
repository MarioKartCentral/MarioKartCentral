<script lang="ts">
  export let country_code: string | null;
  export let size: "large" | "small" = "large"
</script>

<span>
  <!-- <img src={'/src/lib/assets/flags/' + country_code?.toUpperCase() + '.png'} alt={country_code} class="flag {size}" /> -->
  <img src={'https://raw.githubusercontent.com/gosquared/flags/refs/heads/master/flags/flags-iso/flat/64/' + country_code?.toUpperCase() + '.png'} alt={country_code} class="flag {size}" />
</span>

<style>
  img.flag {
    display: inline;
  }
  .large {
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
  }
  .small {
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
  }
</style>
