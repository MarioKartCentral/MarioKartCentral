<script lang="ts">
  import Input from './Input.svelte';
  import { tick } from 'svelte';

  export let fc = '';
  export let name = 'fc';
  export let selected_type: string | null = 'switch';
  export let required = false;

  async function updateFC(e: Event) {
    if (selected_type === 'nnid') return;
    let numbers = fc.replace(/\D/g, '');
    let end_dash = fc.charAt(fc.length - 1);

    let old_fc = fc;
    let new_fc = numbers.slice(0, 4);
    if (numbers.length > 4) {
      new_fc += '-';
    }
    new_fc += numbers.slice(4, 8);
    if (numbers.length > 8) {
      new_fc += '-';
    }
    new_fc += numbers.slice(8, 12);
    if ((numbers.length == 4 || numbers.length == 8) && end_dash === '-') {
      new_fc += '-';
    }

    fc = new_fc;
    if (e.target) {
      const input = e.target as HTMLInputElement;
      const cursor_position = input.selectionStart;
      await tick();
      const new_cursor_position = Number(cursor_position) + (new_fc.length - old_fc.length);
      input.setSelectionRange(new_cursor_position, new_cursor_position);
    }
  }
</script>

<Input
  type={selected_type === 'nnid' ? 'text' : 'tel'}
  bind:value={fc}
  {name}
  placeholder={selected_type !== 'nnid' ? '0000-0000-0000' : 'NNID'}
  on:input={(e) => updateFC(e)}
  minlength={selected_type === 'nnid' ? 6 : 14}
  maxlength={selected_type === 'nnid' ? 16 : 14}
  {required}
/>
