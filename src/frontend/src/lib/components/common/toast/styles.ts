import type { ComponentType } from 'svelte';
import type { ToastItem } from '$lib/stores/toast.svelte';
import { CheckCircleSolid, ExclamationCircleSolid } from 'flowbite-svelte-icons';

type ToastStyle = {
  accent: string;
  icon: ComponentType;
};

type Styles = { [k in ToastItem['color']]: ToastStyle };

const styles: Styles = {
  danger: {
    accent: 'rgb(155, 28, 28)', // red-800
    icon: ExclamationCircleSolid,
  },
  success: {
    accent: 'rgb(22, 101, 52)', // primary-800
    icon: CheckCircleSolid,
  },
};

export { styles };
