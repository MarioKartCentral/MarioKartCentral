import type { LayoutLoad } from './$types';
import type { Locales } from '$i18n/i18n-types';
import { loadLocaleAsync } from '$i18n/i18n-util.async';

export const csr = true;
export const prerender = true;
export const trailingSlash = 'never';

export const load: LayoutLoad = async ({ params }) => {
  const lang = params.lang as Locales;
  await loadLocaleAsync(lang);
  return { locale: lang, activeNavItem: null };
};
