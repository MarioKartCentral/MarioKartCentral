<script lang="ts">
    import LL from "$i18n/i18n-svelte";

    export let language = 'en-us';

    const languages = [
      { value: 'de', getLang: 'DE' },
      { value: 'en-gb', getLang: 'EN_GB' },
      { value: 'en-us', getLang: 'EN_US' },
      { value: 'fr', getLang: 'FR' },
      { value: 'es', getLang: 'ES' },
      { value: 'ja', getLang: 'JA' },
    ];
</script>

<select name="language" value={language}>
    {#each languages as l}
      <option value={l.value}>{$LL.LANGUAGES[l.getLang]()}</option>
    {/each}
</select>