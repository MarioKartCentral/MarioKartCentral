<script lang="ts">
    import Button from "./buttons/Button.svelte";
    import { ArrowLeftOutline, ArrowRightOutline } from "flowbite-svelte-icons";
    export let currentPage: number;
    export let totalPages: number;
    export let refresh_function: Function;

    function decreasePage() {
        if(currentPage > 1) {
            currentPage -= 1;
            refresh_function();
        }
    }

    function increasePage() {
        if(currentPage < totalPages) {
            currentPage += 1;
            refresh_function();
        }
    }
</script>

{#if totalPages > 1}
    <div class="page-select">
        {#if currentPage > 1}
        <Button on:click={decreasePage} circle={true}>
            <ArrowLeftOutline class="w-6 h-6"/>
        </Button>
        {/if}
        
        
        <div class="pages">
            {currentPage} / {totalPages}
        </div>
        
        {#if currentPage < totalPages}
            <Button on:click={increasePage} circle={true}>
                <ArrowRightOutline class="w-6 h-6"/>
            </Button>
        {/if}
        
    </div>
{/if}


<style>
    div.page-select {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: auto;
    }
    div.pages {
        margin: 10px;
        font-weight: bold;
    }
</style>
