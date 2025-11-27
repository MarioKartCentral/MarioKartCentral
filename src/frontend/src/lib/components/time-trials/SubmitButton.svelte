<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import { check_permission, permissions } from '$lib/util/permissions';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { PlusOutline, LockOutline } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';
  import type { UserInfo } from '$lib/types/user-info';

  // Props
  export let game: string | undefined = undefined;
  export let track: string | undefined = undefined;
  export let color:
    | 'none'
    | 'red'
    | 'green'
    | 'blue'
    | 'yellow'
    | 'purple'
    | 'light'
    | 'dark'
    | 'primary'
    | 'alternative' = 'primary';
  export let size: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'md';
  export let extra_classes: string = 'flex items-center gap-2 whitespace-nowrap';

  // Reactive user info
  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  // Check if user has permission to submit time trials (checkDeniedOnly mode)
  $: hasSubmitPermission = user_info?.id !== null && check_permission(user_info, permissions.submit_time_trial, true);

  // Build the submit URL with optional game and track parameters
  $: submitUrl = (() => {
    let url = `/${$page.params.lang}/time-trials/submit`;
    const params = new URLSearchParams();

    if (game) params.set('game', game);
    if (track) params.set('track', track);

    const queryString = params.toString();
    return queryString ? `${url}?${queryString}` : url;
  })();

  // Show different button states based on user permissions
  $: buttonState = (() => {
    if (user_info?.id === null) {
      return {
        icon: LockOutline,
        text: $LL.TIME_TRIALS.LOGIN_TO_SUBMIT(),
        disabled: true,
        color: 'alternative' as const,
        show: true,
      };
    } else if (!hasSubmitPermission) {
      // Hide button if user doesn't have permission
      return {
        href: undefined,
        icon: LockOutline,
        text: '',
        disabled: true,
        color: 'alternative' as const,
        show: false,
      };
    } else {
      return {
        href: submitUrl,
        icon: PlusOutline,
        text: $LL.TIME_TRIALS.SUBMIT_TIME(),
        disabled: false,
        color: color,
        show: true,
      };
    }
  })();
</script>

{#if buttonState.show}
  <Button color={buttonState.color} {size} href={buttonState.href} disabled={buttonState.disabled} {extra_classes}>
    <svelte:component this={buttonState.icon} class="w-4 h-4" />
    {buttonState.text}
  </Button>
{/if}
