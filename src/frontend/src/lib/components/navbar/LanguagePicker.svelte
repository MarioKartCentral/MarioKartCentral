<script lang="ts">
  import { GlobeSolid, ChevronDownSolid } from 'flowbite-svelte-icons';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '../common/DropdownItem.svelte';

  const languages = [
    { value: 'de', nativeName: 'Deutsch' },
    { value: 'en-gb', nativeName: 'English (GB)' },
    { value: 'en-us', nativeName: 'English (US)' },
    { value: 'es', nativeName: 'Español' },
    { value: 'fr', nativeName: 'Français' },
    { value: 'ja', nativeName: '日本語' },
  ];

  const sortedLanguages = [...languages].sort((a, b) => a.nativeName.localeCompare(b.nativeName));
  $: currentLanguage = languages.find((lang) => lang.value === $page.params.lang) || languages[0];

  async function setLanguage(lang: string) {
    const endpoint = '/api/user/settings/editLanguage';
    const payload = {
      language: lang,
    };
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (response.status !== 200) {
      const result = await response.json();
      alert(`${$LL.NAVBAR.SET_LANGUAGE_FAILED()}: ${result['title']}`);
      return;
    }
    window.location.reload();
  }
</script>

<button class="flex items-center rounded-md focus:outline-none focus:ring-0">
  <GlobeSolid size="md" class="md:mr-2 text-gray-300" />
  <span class="hidden md:inline text-white">{currentLanguage.nativeName}</span>
  <ChevronDownSolid size="sm" class="hidden md:inline ml-1 text-white" />
</button>
<Dropdown>
  {#each sortedLanguages as l}
    <DropdownItem on:click={() => setLanguage(l.value)}>
      <div class="item">
        {l.nativeName}
      </div>
    </DropdownItem>
  {/each}
</Dropdown>

<style>
  .item {
    text-align: center;
  }
</style>
