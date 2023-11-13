<script>
	import Icon from './Icon.svelte';
	
    /**
     * @type {string | any[]}
     */
     export let rows;
    /**
     * @type {number}
     */
     export let perPage;
	  export let trimmedRows;

    $: totalRows = rows.length 
    $: currentPage = 0
    $: totalPages = Math.ceil(totalRows / perPage) 
    $: start =  currentPage * perPage
    $: end = currentPage === totalPages - 1 ? totalRows - 1 : start + perPage - 1  ;

		$: trimmedRows = rows.slice(start, end + 1);

    $: totalRows, currentPage = 0
    $: currentPage, start, end

</script>

    {#if totalRows && totalRows > perPage}
        <div class='pagination'>
            <button on:click={() => currentPage -= 1} 
                disabled={currentPage === 0 ? true : false} 
                aria-label="left arrow icon" 
                aria-describedby="prev">
                    <Icon name = 'arrow' direction="s" />
            </button>
            <span id='prev' class='sr-only'>Load previous {perPage} rows</span>
            <p>{start + 1} - {end + 1} of {totalRows}</p>
            <button on:click={() => currentPage += 1} 
                disabled={currentPage === totalPages - 1 ? true : false} 
                aria-label="right arrow icon" 
                aria-describedby="next">
                <Icon name = 'arrow' direction='n' />
            </button>
            <span id='next' class='sr-only'>Load next {perPage} rows</span>
        </div>
    {/if}


<style>
    .sr-only {
      position: absolute;
      clip: rect(1px, 1px, 1px, 1px);
      padding: 0;
      border: 0;
      height: 1px;
      width: 1px;
      overflow: hidden;
    }
    
    .pagination {
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: all;
    }

    .pagination p {
        margin: 0 1rem;
    }

    .selected {
        background-color: var(--accent-color)
    }
	
	button {
		display: flex;
	}
	
</style>