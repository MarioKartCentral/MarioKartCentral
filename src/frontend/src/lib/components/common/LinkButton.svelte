<script lang="ts">
    export let href: string;
</script>

<a href={href}><slot/></a>

<style>
    a {
        text-decoration: none;
        color: white;
        transition: background-color .2s ease-in;
        background-color: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 5px 10px;
    }
    a:hover {
        color: white;
        background-color: rgba(255, 255, 255, 0.4);
        
    }
</style>