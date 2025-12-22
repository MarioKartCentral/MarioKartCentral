import { getContext, setContext } from 'svelte';
import type { Writable } from 'svelte/store';
import { writable } from 'svelte/store';
import { goto } from '$app/navigation';

type Redirect = {
  href: string;
  isCancellable: boolean;
};

export type ToastItem = {
  id: number;
  color: 'success' | 'danger';
  hidden: boolean;
  message: string;
  duration?: number; // in milliseconds
  redirect: Redirect | null;
  timeoutId?: number;
};

function getNotificationDuration(toastItem: Partial<ToastItem>) {
  if (toastItem.duration) return toastItem.duration;
  if (toastItem.redirect) return 3000;
  return 10000;
}

type ToastCreate = Pick<ToastItem, 'color' | 'message'> & Partial<Pick<ToastItem, 'redirect' | 'duration'>>;

class Toast {
  items: Writable<ToastItem[]> = writable([]);

  push = (toastParams: ToastCreate) => {
    this.items.update((items) => {
      const toastItem = { id: items.length, hidden: false, redirect: null, ...toastParams };
      const timeout = getNotificationDuration(toastItem);
      const timeoutId = setTimeout(() => {
        if (toastItem.redirect) {
          goto(toastItem.redirect.href);
        }
        this.set(toastItem.id, { hidden: true });
      }, timeout);
      return [...items, { ...toastItem, timeoutId }];
    });
  };

  set = (toastId: number, toastParams: Pick<ToastItem, 'hidden'> & Partial<Pick<ToastItem, 'timeoutId'>>) => {
    this.items.update((items) => {
      const toast = items.find((item) => item.id === toastId);
      if (!toast) throw Error('Invalid toast ID specified');
      if (toastParams.timeoutId === undefined) {
        clearTimeout(toast.timeoutId);
      }
      return items.map((item) => (item.id === toastId ? { ...toast, ...toastParams } : item));
    });
  };
}

const TOAST_KEY = Symbol('toastState');
export function setToastState() {
  return setContext(TOAST_KEY, new Toast());
}
export function getToastState() {
  return getContext<Toast>(TOAST_KEY);
}
