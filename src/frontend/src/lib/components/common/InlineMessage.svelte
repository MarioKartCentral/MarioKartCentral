<script lang="ts">
  import type { ComponentType, ComponentProps } from 'svelte';
  import Caution from '../icons/Caution.svelte';
  import { InfoCircleOutline, ExclamationCircleOutline, CheckCircleOutline } from 'flowbite-svelte-icons';

  type Status = 'success' | 'warn' | 'error';
  type StatusIcon<T extends ComponentType> = {
    component: T;
    props: ComponentProps<InstanceType<T>>;
  };

  type StatusMessageInfo = {
    icon:
      | StatusIcon<typeof InfoCircleOutline>
      | StatusIcon<typeof CheckCircleOutline>
      | StatusIcon<typeof Caution>
      | StatusIcon<typeof ExclamationCircleOutline>;
    role: 'status' | 'alert';
    classes: {
      color: string;
    };
  };
  export let iconSize: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'md';
  export let status: Status;
  export let hidden: boolean = false;
  export let ariaLabel: string | undefined = undefined;

  const icons: Record<Status, StatusMessageInfo> = {
    success: {
      icon: {
        component: CheckCircleOutline,
        props: { size: iconSize, 'aria-hidden': true },
      },
      role: 'status',
      classes: {
        color: 'text-primary-500',
      },
    },
    warn: {
      icon: {
        component: Caution,
        props: {
          size: iconSize,
          outlineColor: 'oklch(82.8% 0.189 84.429)',
          textColor: 'oklch(82.8% 0.189 84.429)',
          fill: 'none',
          'aria-hidden': true,
        },
      },
      role: 'alert',
      classes: {
        color: 'text-amber-400',
      },
    },
    error: {
      icon: {
        component: ExclamationCircleOutline,
        props: { size: iconSize, 'aria-hidden': true },
      },
      role: 'alert',
      classes: {
        color: 'text-red-500',
      },
    },
  };
  $: iconStatus = icons[status];
  $: containerClasses = ['status text-sm', iconStatus.classes.color].join(' ').trim();
</script>

<span role={iconStatus.role}>
  {#if !hidden}
    <div class={containerClasses}>
      <svelte:component this={iconStatus.icon.component} {...iconStatus.icon.props} />
      <span aria-label={ariaLabel} class:sr-only={!$$slots.default}>
        <slot />
      </span>
    </div>
  {/if}
</span>

<style>
  .status {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }
</style>
