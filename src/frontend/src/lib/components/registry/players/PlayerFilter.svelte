<script lang="ts">
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
  <input bind:value={filters.name} type='text'>
</div>
