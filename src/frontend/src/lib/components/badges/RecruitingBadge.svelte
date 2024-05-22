<script lang="ts">
  import Badge from "./Badge.svelte";

  export let recruiting: string;
  const recruitingStr = recruiting == '1' ? 'Recruiting' :  'Not Recruiting'
  const recruitingId = recruiting == '1' ? 'recruiting' :  'not_recruiting'
</script>

<Badge badgeClass={recruitingId + '_badge wide'}>{recruitingStr}</Badge>

<style>

  :global(.recruiting_badge) {
    background-color: #00997b;
    border: 1px solid #006b5c;
  }

  :global(.not_recruiting_badge) {
    background-color: #7f7f80;
    border: 1px solid #4b4b4b;
  }
</style>
