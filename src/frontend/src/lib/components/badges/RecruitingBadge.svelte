<script lang="ts">
  import Badge from './Badge.svelte';
  import LL from '$i18n/i18n-svelte';

  export let recruiting: boolean;
</script>

<Badge badgeClass={(recruiting ? 'recruiting' : 'not_recruiting') + '_badge wide'}>
  {recruiting
    ? $LL.TEAMS.PROFILE.RECRUITMENT_STATUS.RECRUITING()
    : $LL.TEAMS.PROFILE.RECRUITMENT_STATUS.NOT_RECRUITING()}
</Badge>
