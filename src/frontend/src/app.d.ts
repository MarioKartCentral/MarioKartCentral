/// <reference types="@sveltejs/kit" />

type Locales = import('$i18n/i18n-types').Locales;

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare namespace App {
  interface Locals {
    lang: Locales;
  }
  // interface Platform {}
  // interface Session { }
  // interface Stuff {}
}
