/// <reference types="@sveltejs/kit" />

// See https://kit.svelte.dev/docs/types#app for information about these interfaces
declare namespace App {
  interface PageData {
    activeNavItem: 'TOURNAMENTS' | 'TIME TRIALS' | 'LOUNGE' | 'REGISTRY' | 'MODERATOR' | null;
  }
}
