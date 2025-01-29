<script lang="ts">
    export let linkText: string | null = null;
    export let link: string | null = null;
    export let isTopRow = false;

    const rowCss = isTopRow ? 'top-row' : 'bottom-row'
</script>

<div class="wrapper">
    <div class="{rowCss}">
        <slot />
    </div>
    <div class="mt-[10px] mb-[10px] h-[20px] text-center">
        {#if link && linkText}
                <a
                    class="hover:text-emerald-400 p-1 font-medium"
                    href={link}>
                    {linkText}
                </a>
        {/if}
    </div>
</div>

<style>
    .wrapper {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .top-row {
        height: 575px;
    }
    .bottom-row {
        height: 500px;
    }
</style>