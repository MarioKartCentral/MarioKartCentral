<script lang="ts">
    import Button from "./buttons/Button.svelte";
    import { ArrowLeftOutline, ArrowRightOutline } from "flowbite-svelte-icons";
    export let currentPage: number;
    export let totalPages: number;
    export let refresh_function: () => void;

    $: input_number = currentPage;
    
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

    function updatePageFromInput() {
        if(input_number < 1) {
            input_number = currentPage;
            return;
        }
        if(input_number > totalPages) {
            input_number = currentPage;
            return;
        }
        currentPage = input_number;
        refresh_function();
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
            <input type="number" min=1 max={totalPages} bind:value={input_number} on:blur={updatePageFromInput}/>
            / {totalPages}
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
        display: flex;
        align-items: center;
        margin: 10px;
        font-weight: bold;
        gap: 10px;
    }
    input[type=number] {
        width: 50px;
    }
</style>
