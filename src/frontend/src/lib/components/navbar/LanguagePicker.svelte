<script lang="ts">
    import { GlobeSolid } from "flowbite-svelte-icons";
    import LL from "$i18n/i18n-svelte";
    import Dropdown from "$lib/components/common/Dropdown.svelte";
    import DropdownItem from "../common/DropdownItem.svelte";

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
        if(response.status !== 200) {
            const result = await response.json();
            alert(`${$LL.NAVBAR.SET_LANGUAGE_FAILED()}: ${result['title']}`);
            return;
        }
        window.location.reload();
    }
</script>

<GlobeSolid size="xl" class="text-gray-300"/>
<Dropdown>
    {#each languages as l}
        <DropdownItem on:click={() => setLanguage(l.value)}>
            <div class="item">
                {language_strings[l.getLang]()}
            </div>
        </DropdownItem>
    {/each}
</Dropdown>

<style>
    .item {
        text-align: center;
    }
</style>