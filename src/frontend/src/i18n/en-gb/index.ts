import en_us from '../en-us';
import { extendDictionary } from 'typesafe-i18n/utils';

const en_gb = extendDictionary(en_us, {
  LANGUAGE: 'British English',
});

export default en_gb;
