<script lang="ts">
  export let country_code: string | null;
  export let size: 'large' | 'small' = 'large';

  const flags = import.meta.glob<string>('../../assets/flags/*.png', { query: { url: true }, import: 'default' });

  const getFlag = async (code: string) => {
    const path = `../../assets/flags/${code.toUpperCase()}.png`;
    const module = await flags[path]?.();
    return module;
  };

  let flagUrl = '';

  $: if (country_code) {
    getFlag(country_code).then((url) => {
      flagUrl = url || '';
    });
  }
</script>

<span>
  <img src={flagUrl} alt={country_code} class="flag {size}" />
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
