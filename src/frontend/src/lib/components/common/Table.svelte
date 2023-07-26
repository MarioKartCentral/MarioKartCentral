<table>
   <slot/> 
</table>

<style>
    table {
        background-color: rgba(127, 127, 127, 0.6);
        border-collapse: collapse;
        width: 100%;
    }
    table :global(thead) {
        background-color: rgb(0, 128, 0, 0.6);
    }
    table :global(td) {
        padding: 10px;
        text-align: center;
    }
    /* Alternating row background colors: in an each block,
        put the class name as row-{i%2} */
    table :global(.row-1) {
        background-color:rgba(192, 192, 192, 0.6);
    }
</style>