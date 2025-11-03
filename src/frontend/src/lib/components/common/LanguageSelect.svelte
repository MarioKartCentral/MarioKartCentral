<script lang="ts">
  import LL from '$i18n/i18n-svelte';

  export let language = 'en-us';

  const languages = [
    { value: 'de', getLang: 'DE' },
    { value: 'en-gb', getLang: 'EN_GB' },
    { value: 'en-us', getLang: 'EN_US' },
    { value: 'fr', getLang: 'FR' },
    { value: 'es', getLang: 'ES' },
    { value: 'ja', getLang: 'JA' },
  ];

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const language_strings: any = $LL.LANGUAGES;
</script>

<select name="language" value={language}>
  {#each languages as l (l.value)}
    <option value={l.value}>{language_strings[l.getLang]()}</option>
  {/each}
</select>
