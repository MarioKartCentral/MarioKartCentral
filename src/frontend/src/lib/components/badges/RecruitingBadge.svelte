<script lang="ts">
  import Badge from "./Badge.svelte";

  export let recruiting: string;
  const recruitingStr = recruiting == '1' ? 'Recruiting' :  'Not Recruiting'
  const recruitingId = recruiting == '1' ? 'recruiting' :  'not_recruiting'
</script>

<Badge badgeClass={recruitingId + '_badge wide'}>{recruitingStr}</Badge>