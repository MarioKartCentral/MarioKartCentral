<script lang="ts">
  import { country_codes } from "$lib/stores/country_codes";
  export let filters;
  const list = [
    { value: '', label: 'Show All' },
    { value: 'mk8dx', label: 'Show with MK8DX FC' },
    { value: 'mkw', label: 'Show with MKW FC' },
    { value: 'mkt', label: 'Show with MKT FC' },
    { value: 'mk7', label: 'Show with 3DS FC' },
    { value: 'mk8', label: 'Show with NNID' },
  ];
</script>

<div>
  <select bind:value={filters.game}>
    {#each list as { value, label }}
      <option value={value}>{label}</option>
    {/each}
  </select>
  <select bind:value={filters.country}>
    <option value={null}></option>
    {#each country_codes as country_code}
      <option value={country_code}>{country_code}</option>
    {/each}
  </select>
  <input bind:value={filters.name} type='text' placeholder="name">
</div>
