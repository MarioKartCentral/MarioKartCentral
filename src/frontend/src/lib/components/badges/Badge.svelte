<script lang="ts">
    import './badge_styles.css';
    export let badgeClass = "";
    export let style = "";
</script>

<span class="badge {badgeClass}" style={style}>
    <slot/>
</span>