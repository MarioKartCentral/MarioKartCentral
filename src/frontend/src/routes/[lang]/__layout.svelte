<script context="module" lang="ts">
  import type { Load } from '@sveltejs/kit';
  import type { Locales } from '$i18n/i18n-types';
  import { loadLocaleAsync } from '$i18n/i18n-util.async';

  type LoadParams = {
    lang: Locales;
  };

  export const load: Load<LoadParams> = async ({ params }) => {
    const lang = params.lang;
    await loadLocaleAsync(lang);
    return { props: { locale: lang } };
  };
</script>

<script lang="ts">
  import { setLocale } from '$i18n/i18n-svelte';
  export let locale: Locales;
  setLocale(locale);
</script>

<slot />
