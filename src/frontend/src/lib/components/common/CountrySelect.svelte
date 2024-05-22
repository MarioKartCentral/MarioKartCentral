<script lang="ts">
    import { country_codes } from "$lib/stores/country_codes";
    import LL from "$i18n/i18n-svelte";

    export let value: string | null = null;
    export let is_filter = false; // used to determine whether null/all countries is a select option

    type Country = {
        country_code: string,
        translated_name: string
    };

    let countries: Country[] = [];

    for(let country_code of country_codes) {
        countries.push(
            {
                country_code: country_code,
                translated_name: $LL.COUNTRIES[country_code]()
            }
        );
    }
    countries.sort((a, b) => a.translated_name.localeCompare(b.translated_name));
</script>

<select class="country" bind:value={value}>
    {#if is_filter}
        <option value={null}>{$LL.PLAYER_LIST.FILTERS.ALL_COUNTRIES()}</option>
    {/if}
    {#each countries as country}
        <option value={country.country_code}>{country.translated_name}</option>
    {/each}
</select>

<style>
    .country {
        width: 200px;
    }
</style>