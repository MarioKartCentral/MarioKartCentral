<script lang="ts">
  // ⚠️ icon
  import { twMerge } from 'tailwind-merge';
  const sizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8',
  };
  export let size: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'md';
  export let role = 'img';
  export let ariaLabel = 'caution solid';
  export let textColor = 'white';
  export let outlineColor = 'white';
  export let fill = 'currentColor';

  // outline credit: https://weareoutman.github.io/rounded-polygon/
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  fill="none"
  {...$$restProps}
  class={twMerge('shrink-0', sizes[size], $$props.class)}
  {role}
  aria-label={ariaLabel}
  viewBox="0 0 24 24"
  on:click
  on:keydown
  on:keyup
  on:focus
  on:blur
  on:mouseenter
  on:mouseleave
  on:mouseover
  on:mouseout
>
  <path
    stroke-linejoin="round"
    stroke-width="2"
    stroke={outlineColor}
    {fill}
    d="M8.5358983848622 3.8756443470179a4 4 0 0 1 6.9282032302755 0l7.0717967697245 12.248711305964a4 4 0 0 1 -3.4641016151378 6l-14.143593539449 0a4 4 0 0 1 -3.4641016151378 -6 Z"
  />
  <path
    fill={textColor}
    d="M 10.67 17 a 1.335 1.335 0 1 1 2.67 0 a 1.335 1.335 0 0 1 -2.67 0 M 10.67 8.5 a 1.335 1.335 0 1 1 2.67 0 l -0.475 5.5 a 0.86 0.86 0 0 1 -1.72 0 z"
  />
</svg>

<!--
@component
## Props
@prop export let size: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'md';
@prop export let role = 'img';
@prop export let ariaLabel = 'caution solid';
@prop export let textColor = 'white';
@prop export let outlineColor = 'white';

-->
