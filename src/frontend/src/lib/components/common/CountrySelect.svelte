<script lang="ts">
    import { country_codes } from "$lib/stores/country_codes";
    import LL from "$i18n/i18n-svelte";

    export let value: string | null = null;
    export let is_filter = false; // used to determine whether null/all countries is a select option
    export let is_required = false;

    type Country = {
        country_code: string,
        translated_name: string
    };

    let countries: Country[] = [];

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const country_strings: any = $LL.COUNTRIES;

    for(let country_code of country_codes) {
        countries.push(
            {
                country_code: country_code,
                translated_name: country_strings[country_code]()
            }
        );
    }
    countries.sort((a, b) => a.translated_name.localeCompare(b.translated_name));
</script>

<select class="country" name="country" bind:value={value} required={is_required}>
    {#if is_filter}
        <option value={null}>{$LL.COUNTRIES.ALL()}</option>
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