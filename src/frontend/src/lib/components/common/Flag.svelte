<script lang="ts">
  export let country_code: string | null;
  export let size: "large" | "small" = "large"
</script>

<span>
  <img src={'/src/lib/assets/flags/' + country_code?.toUpperCase() + '.png'} alt={country_code} class="flag {size}" />
</span>

<style>
  img.flag {
    display: inline;
  }
  .large {
    max-height: 36px;
  }
  .small {
    max-height: 26px;
  }
</style>
