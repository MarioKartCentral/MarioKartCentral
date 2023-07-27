<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { goto } from '$app/navigation';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  async function register(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    const payload = { email: data.get('email')!.toString(), password: data.get('password')!.toString() };

    const isLogin = false;
    const endpoint = '/api/user/signup';
    console.log({ data, isLogin, endpoint });
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.status < 300) {
      goto('/');
    } else {
      alert('Registration failed');
    }
  }
</script>

<h2>Register</h2>
<form method="post" on:submit|preventDefault={register}>
  <div>
    <label for="email">Email</label>
    <input name="email" type="email" />
  </div>
  <div>
    <label for="password">Password</label>
    <input name="password" type="password" />
  </div>
  <button class="register-btn">Register</button>
</form>
