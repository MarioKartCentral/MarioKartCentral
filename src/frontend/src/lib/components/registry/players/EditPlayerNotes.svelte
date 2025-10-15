<script lang="ts">
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { createEventDispatcher } from 'svelte';

  export let playerId: number;
  export let notes = '';

  let newNotes = notes;
  const dispatch = createEventDispatcher<{ cancel: null }>();

  async function editNotes(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    const payload = {
      notes: `${data.get('notes') || ''}`.trim(),
    };

    const endpoint = `/api/registry/players/${playerId}/notes`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (response.status !== 200) {
      const result = await response.json();
      const detail = result.detail ? `, ${result.detail}` : '';
      alert(`${result.title}${detail}`);
    } else {
      window.location.href = $page.url.href;
    }
  }
  async function handleCancel() {
    dispatch('cancel');
  }
</script>

<form on:submit|preventDefault={editNotes}>
  <div>
    <label for="notes">{$LL.PLAYERS.PROFILE.PLAYER_NOTES()}</label> <br />
    <textarea name="notes" class="w-full h-28" bind:value={newNotes}></textarea>
  </div>
  <br />
  <Button type="submit" disabled={newNotes.trim() === notes}>{$LL.COMMON.SAVE()}</Button>
  <Button color="red" on:click={handleCancel}>{$LL.COMMON.CANCEL()}</Button>
  <Button color="dark" extra_classes="float-right" on:click={() => (newNotes = '')}
    >{$LL.PLAYERS.PROFILE.CLEAR()}</Button
  >
</form>
