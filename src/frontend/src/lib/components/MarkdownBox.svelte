<script lang="ts">
    export let title: string;
    export let content: string;
</script>

<div class="container">
    <div class="header">
        {title}
    </div>
    <div class="content">
        {content}
    </div>
</div>

<style>
    .container {
        width: 50%;
        margin: 20px auto 20px auto;
    }
</style>