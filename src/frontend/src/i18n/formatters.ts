import type { FormattersInitializer } from 'typesafe-i18n';
import type { Locales, Formatters } from './i18n-types';
import { uppercase } from 'typesafe-i18n/formatters';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const initFormatters: FormattersInitializer<Locales, Formatters> = (locale: Locales) => {
  const formatters: Formatters = {
    // add your formatter functions here
    // @ts-expect-error suppress warning
    bold: (val: string) => `<strong>${val}</strong>`,
    // @ts-expect-error suppress warning
    uppercase,
    // @ts-expect-error suppress warning
    parsedate: (val: string) => {
      if (!val.startsWith('DATE-')) return val;
      const timestamp = parseInt(val.replace('DATE-', '')) * 1000;
      return new Date(timestamp).toLocaleString(locale, { dateStyle: 'medium', timeStyle: 'short' });
    },
  };

  return formatters;
};
