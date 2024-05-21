<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
    import Button from '$lib/components/common/buttons/Button.svelte';
  export let userId = 'Loading...';
  export let playerId = '';
  export let isLoggedIn = false;

  onMount(async () => {
    const res = await fetch(`/api/user/me`);
    if (res.status === 200) {
      const body = await res.json();
      userId = body['id'];
      playerId = body['player_id'] || 'User has not completed player registration';
      isLoggedIn = true;
    } else {
      userId = 'Not logged in';
      playerId = 'N/A';
      isLoggedIn = false;
    }
  });

  async function loginOrSignup(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const payload = { email: data.get('email')!.toString(), password: data.get('password')!.toString() };

    const isLogin = event.submitter?.classList.contains('login-btn') ?? false;
    const endpoint = isLogin ? '/api/user/login' : '/api/user/signup';
    console.log({ data, isLogin, endpoint });
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (response.status < 300) {
      goto('/');
    } else {
      alert(`${isLogin ? 'Login' : 'Registration'} failed`);
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async function logout(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const response = await fetch('/api/user/logout', { method: 'POST' });

    if (response.status < 300) {
      goto('/');
    } else {
      alert('Logout failed');
    }
  }
</script>

<svelte:head>
  <title>Mario Kart Central</title>
</svelte:head>

<h1>{$LL.WELCOME()}</h1>
<p>{$LL.SUMMARY()}</p>
<p>{$LL.PLAYER_PROFILE.LANGUAGE()}: {$LL.LANGUAGE()}</p>

<p>User ID: {userId}</p>
<p>Player ID: {playerId}</p>
{#if isLoggedIn}
  <form method="post" on:submit|preventDefault={logout}>
    <Button type="submit">{$LL.LOGOUT()}</Button>
  </form>
{:else}
  <form method="post" on:submit|preventDefault={loginOrSignup}>
    <div>
      <label for="email">{$LL.EMAIL()}</label>
      <input name="email" type="email" />
    </div>
    <div>
      <label for="password">{$LL.PASSWORD()}</label>
      <input name="password" type="password" />
    </div>
    <button class="login-btn">{$LL.NAVBAR.LOGIN()}</button>
    <button class="register-btn">{$LL.NAVBAR.REGISTER()}</button>
  </form>
{/if}
