<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { goto } from '$app/navigation';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  async function login(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const payload = { email: data.get('email')!.toString(), password: data.get('password')!.toString() };

    const isLogin = true;
    const endpoint = '/api/user/login';
    console.log({ data, isLogin, endpoint });
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (response.status < 300) {
      goto('/');
    } else {
      alert(`Login failed`);
    }
  }
</script>

{#if user_info.id !== null}
  Already logged in
{:else}
  <h2>Login</h2>
  <form method="post" on:submit|preventDefault={login}>
    <div>
      <label for="email">Email</label>
      <input name="email" type="email" />
    </div>
    <div>
      <label for="password">Password</label>
      <input name="password" type="password" />
    </div>
    <button class="login-btn">Log in</button>
  </form>
{/if}
