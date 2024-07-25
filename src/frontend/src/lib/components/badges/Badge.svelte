<script lang="ts">
    import './badge_styles.css';
    export let badgeClass = "";
    export let style = "";
</script>

<span class={badgeClass} style={style}>
    <slot/>
</span>

<style>
span {
    display: inline-block;
    text-align: center;
    color: white;
    border-radius: 4px;
    padding: 2px 6px;
    /* margin: 2px; */
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans',
    sans-serif;
    font-size: 13px;
    min-width: 50px;
}
.mid {
    width: 75px;
}
.wide {
    width: 100px;
}
</style>