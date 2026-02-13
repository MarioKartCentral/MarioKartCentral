<script lang="ts">
  type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  export let size: Size = 'md';
  const sizes: Record<Size, number> = {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 28,
  };

  $: value = sizes[size];
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  width={value}
  height={value}
  fill="currentColor"
  class="bi bi-twitch"
  viewBox="0 0 16 16"
  aria-hidden="true"
>
  <path
    d="M3.857 0 1 2.857v10.286h3.429V16l2.857-2.857H9.57L14.714 8V0zm9.714 7.429-2.285 2.285H9l-2 2v-2H4.429V1.143h9.142z"
  />
  <path d="M11.857 3.143h-1.143V6.57h1.143zm-3.143 0H7.571V6.57h1.143z" />
</svg>
