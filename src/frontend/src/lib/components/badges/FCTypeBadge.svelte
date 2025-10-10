<script lang="ts">
  import Badge from './Badge.svelte';
  import LL from '$i18n/i18n-svelte';

  export let type: string;
  export let style = '';

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const type_strings: any = $LL.FRIEND_CODES.TYPES;
</script>

<Badge badgeClass="fc_type_{type}_badge wide" {style}>{type_strings[type.toUpperCase()]()}</Badge>
