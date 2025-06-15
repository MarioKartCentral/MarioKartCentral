<!-- Validation Status Filter Component -->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    
    export let value: string = 'all';
    export let showCounts: boolean = false;
    export let counts: Record<string, number> = {};
    export let size: 'sm' | 'md' | 'lg' = 'md';
    export let disabled: boolean = false;
    
    const dispatch = createEventDispatcher<{
        change: string;
    }>();
    
    const options = [
        { value: 'all', label: 'All Records', description: 'Show all time trial records' },
        { value: 'validated_only', label: 'Validated Only', description: 'Only show records with all proofs validated' },
        { value: 'unvalidated_only', label: 'Pending Validation', description: 'Records with proofs awaiting validation' },
        { value: 'proofless', label: 'No Proof', description: 'Records without proof submissions' },
    ];
    
    function handleChange() {
        dispatch('change', value);
    }
    
    function getCountDisplay(optionValue: string): string {
        if (!showCounts || !counts[optionValue]) return '';
        return ` (${counts[optionValue].toLocaleString()})`;
    }
    
    function getSizeClasses() {
        switch (size) {
            case 'sm':
                return 'text-sm p-2';
            case 'lg':
                return 'text-lg p-4';
            default:
                return 'text-base p-3';
        }
    }
</script>

<div class="validation-filter">
    <label for="validation-status-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Validation Status
        {#if showCounts && counts.total}
            <span class="text-gray-500">({counts.total.toLocaleString()} total)</span>
        {/if}
    </label>
    
    <select 
        id="validation-status-select"
        bind:value
        on:change={handleChange}
        {disabled}
        class="w-full border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white {getSizeClasses()}"
    >
        {#each options as option}
            <option value={option.value}>
                {option.label}{getCountDisplay(option.value)}
            </option>
        {/each}
    </select>
    
    {#if value !== 'all'}
        <div class="mt-2 text-xs text-gray-600 dark:text-gray-400">
            {options.find(opt => opt.value === value)?.description}
        </div>
    {/if}
</div>

<!-- Quick Filter Buttons (Alternative UI) -->
{#if $$slots.buttons}
    <slot name="buttons" />
{:else if size === 'sm'}
    <div class="flex flex-wrap gap-2 mt-2">
        {#each options as option}
            <button
                type="button"
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors
                       {value === option.value 
                         ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' 
                         : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'}"
                on:click={() => { value = option.value; handleChange(); }}
                {disabled}
            >
                {option.label}
                {#if showCounts && counts[option.value]}
                    <span class="ml-1 text-xs opacity-75">
                        {counts[option.value].toLocaleString()}
                    </span>
                {/if}
            </button>
        {/each}
    </div>
{/if}

<style>
    .validation-filter select:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .validation-filter :global(button:disabled) {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
