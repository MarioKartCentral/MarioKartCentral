<script lang="ts">
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';

  async function changeEmail(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    const payload = {
      new_email: data.get('new_email')?.toString(),
      password: data.get('password')?.toString(),
    };
    const endpoint = '/api/user/change_email';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.status < 300) {
      window.location.reload();
      alert($LL.LOGIN.CHANGE_EMAIL_SUCCESS());
    } else {
      alert(`${$LL.LOGIN.CHANGE_EMAIL_FAILED()}: ${result['title']}`);
    }
  }
</script>

<form on:submit|preventDefault={changeEmail}>
  <div class="option">
    <label for="new_email">{$LL.LOGIN.NEW_EMAIL()}</label>
    <input name="new_email" type="email" required />
  </div>
  <div class="option">
    <label for="password">{$LL.LOGIN.PASSWORD()}</label>
    <input name="password" type="password" required />
  </div>
  <Button type="submit">{$LL.LOGIN.CHANGE_EMAIL()}</Button>
</form>

<style>
  label {
    width: 100px;
  }
  div.option {
    margin-bottom: 10px;
  }
</style>
