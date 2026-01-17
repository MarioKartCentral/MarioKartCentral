import type { Action } from 'svelte/action';

/**
 * Observes focus changes and dispatches a custom `outclick` event if the focussed element is outside the target element or its children.
 *
 * - Add `use:clickOutside` to the element to observe
 * - Listen to the event with `on:outclick`
 * @param node The root element to observe
 * @param active Determines whether the event listener is active. Bindable to a variable with `use:clickOutside={active}`. Defaults to `true`
 */
export const clickOutside: Action<HTMLElement, boolean | undefined, { 'on:outclick': (e: CustomEvent) => void }> = (
  node: HTMLElement,
  active: boolean = true,
) => {
  function checkOutclick(event: MouseEvent | FocusEvent) {
    if (!event.target) throw Error('Event target not found');
    if (node && !node.contains(event.target as Node)) {
      node.dispatchEvent(new CustomEvent('outclick'));
    }
  }

  function addListeners() {
    document.addEventListener('click', checkOutclick);
  }
  function removeListeners() {
    document.removeEventListener('click', checkOutclick);
  }
  if (active) {
    addListeners();
  }
  return {
    destroy: () => {
      removeListeners();
    },
    update: (active) => (active ? addListeners() : removeListeners()),
  };
};
