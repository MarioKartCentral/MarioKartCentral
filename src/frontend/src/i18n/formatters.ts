import type { FormattersInitializer } from 'typesafe-i18n';
import type { Locales, Formatters } from './i18n-types';
import { uppercase } from 'typesafe-i18n/formatters';

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
    ordinalSuffix: (val: number) => ordinalSuffix(val, locale),
  };

  return formatters;
};

function ordinalSuffix(val: number, locale: Locales) {
  // implementations based from https://www.unicode.org/cldr/charts/46/supplemental/language_plural_rules.html
  if (locale === 'en-gb' || locale === 'en-us') {
    return ordinalSuffixEn(val);
  }
  if (locale === 'es') {
    return ordinalSuffixEs(val);
  }
  if (locale === 'fr') {
    return ordinalSuffixFr(val);
  }
  if (locale === 'de') {
    return ordinalSuffixDe(val);
  }
  if (locale === 'ja') {
    return ordinalSuffixJa(val);
  }

  // just return the number if a locale is not implemented
  return val.toString();
}

function ordinalSuffixEn(n: number) {
  if (n % 10 === 1 && n % 100 !== 11) {
    return `${n}st`;
  }
  if (n % 10 === 2 && n % 100 !== 12) {
    return `${n}nd`;
  }
  if (n % 10 === 3 && n % 100 !== 13) {
    return `${n}rd`;
  }
  return `${n}th`;
}

function ordinalSuffixEs(n: number) {
  return `${n}.º`;
}

function ordinalSuffixFr(n: number) {
  if (n === 1) {
    return `${n}er`;
  }
  return `${n}e`;
}

function ordinalSuffixDe(n: number) {
  return `${n}.`;
}

function ordinalSuffixJa(n: number) {
  return `${n}位`;
}
