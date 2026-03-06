import type { FormattersInitializer } from 'typesafe-i18n';
import type { Locales, Formatters } from './i18n-types';
import { uppercase } from 'typesafe-i18n/formatters';
import type { NumberComparison } from './custom-types';

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
    formatNumberComparison: (vals: NumberComparison) => formatNumberComparison(vals, locale),
    toCount: (vals: NumberComparison) => vals.max ?? vals.min ?? 0,
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

function formatNumberComparison(nums: NumberComparison, locale: Locales): string {
  const { min, max } = nums;

  type ComparisonStrings = {
    AT_MOST: string;
    AT_LEAST: string;
    BETWEEN: string;
    EXACTLY: string;
  };
  const strings: Record<Locales, ComparisonStrings> = {
    'en-us': {
      AT_MOST: `at most ${max}`,
      AT_LEAST: `at least ${min}`,
      BETWEEN: `${min}-${max}`,
      EXACTLY: `exactly ${min}`,
    },
    'en-gb': {
      AT_MOST: `at most ${max}`,
      AT_LEAST: `at least ${min}`,
      BETWEEN: `${min}-${max}`,
      EXACTLY: `exactly ${min}`,
    },
    de: {
      AT_MOST: `höchstens ${max}`,
      AT_LEAST: `mindestens ${min}`,
      BETWEEN: `${min}-${max}`,
      EXACTLY: `genau ${min}`,
    },
    es: {
      AT_MOST: `como máximo ${max}`,
      AT_LEAST: `como mínimo ${min}`,
      BETWEEN: `entre ${min}-${max}`,
      EXACTLY: `exactamente ${min}`,
    },
    fr: {
      AT_MOST: `au plus ${max}`,
      AT_LEAST: `au moins ${min}`,
      BETWEEN: `entre ${min} et ${max}`,
      EXACTLY: `exactement ${min}`,
    },
    ja: {
      AT_MOST: `1-${max}`,
      AT_LEAST: `${min}`,
      BETWEEN: `${min}-${max}`,
      EXACTLY: `${min}`,
    },
  };

  const minIsNum = typeof min === 'number';
  const maxIsNum = typeof max === 'number';

  switch (true) {
    case minIsNum && maxIsNum:
      return min === max ? strings[locale].EXACTLY : strings[locale].BETWEEN;
    case minIsNum:
      return strings[locale].AT_LEAST;
    case maxIsNum:
      return strings[locale].AT_MOST;
    default:
      return '';
  }
}
