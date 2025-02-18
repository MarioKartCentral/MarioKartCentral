<script lang="ts">
    import { fc_types } from "$lib/util/util";
    import LL from "$i18n/i18n-svelte";

    export let type: string | null = null;
    export let disabled = false;
    export let flex = false;
    export let required = false;
    export let all_option = false;
    export let hide_labels = false;
    export let disabled_types: string[] = [];

    
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const type_strings: any = $LL.FRIEND_CODES.TYPES;
</script>

<div class={flex ? 'flex' : ''}>
    {#if !hide_labels}
        <div>
            <label for="fc_type">Type</label>
        </div>
    {/if}
    <div>
        <select
            name="fc_type"
            bind:value={type}
            on:change
            {disabled} {required}
            >
            {#if all_option}
                <option value={null} selected>{$LL.FRIEND_CODES.TYPES.ALL()}</option>
            {:else}
                <option value={null} disabled selected>{$LL.FRIEND_CODES.SELECT_TYPE()}</option>
            {/if}
            {#each fc_types as type}
                <option value={disabled_types.includes(type) ? null : type} disabled={disabled_types.includes(type)}>
                    {type_strings[type.toUpperCase()]()}
                </option>
            {/each}
        </select>
    </div>
</div>

<style>
  select {
    width: 192px;
  }
  .flex {
    display: flex;
    align-items: center;
  }
</style>

