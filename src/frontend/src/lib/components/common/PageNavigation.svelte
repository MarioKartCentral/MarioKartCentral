<script lang="ts">
    import Button from "./buttons/Button.svelte";
    import { ArrowLeftOutline, ArrowRightOutline } from "flowbite-svelte-icons";
    export let currentPage: number;
    export let totalPages: number;
</script>

{#if totalPages > 1}
<div class="page-select">
    {#if currentPage > 1}
    <Button on:click={() => (currentPage > 1 ? (currentPage = currentPage - 1) : (currentPage = currentPage))} circle={true}>
        <ArrowLeftOutline class="w-6 h-6"/>
    </Button>
    {/if}
    
    
    <div class="pages">
        {currentPage} / {totalPages}
    </div>
      
    {#if currentPage < totalPages}
        <Button on:click={() => (currentPage < totalPages ? (currentPage = currentPage + 1) : (currentPage = currentPage))} circle={true}>
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
