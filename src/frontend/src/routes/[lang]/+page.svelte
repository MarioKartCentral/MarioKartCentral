<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  export let userEmail = "Loading...";
  export let userRoles : string[] = [];
  export let isLoggedIn = false;

  onMount(async () => {
    const res = await fetch(`/api/user/me`);
    if (res.status === 200) {
      const body = await res.json();
      userEmail = body["email"]
      userRoles = body["roles"]
      isLoggedIn = true;
    } else {
      userEmail = "Not logged in"
      isLoggedIn = false;
    }
  });

  async function loginOrSignup(event: SubmitEvent & {currentTarget: EventTarget & HTMLFormElement}) {
    const data = new FormData(event.currentTarget);
    const payload = { email: data.get("email")!.toString(), password: data.get("password")!.toString() }

    const isLogin = event.submitter?.classList.contains("login-btn") ?? false;
    const endpoint = isLogin ? "/api/user/login" : "/api/user/signup";
    console.log({data, isLogin, endpoint})
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}, 
      body: JSON.stringify(payload) });
    const result = await response.json();

    if (response.status < 300) {
      goto('/');
    } else {
      alert(`${isLogin ? "Login" : "Registration"} failed`);
    }
  }

  async function logout(event: SubmitEvent & {currentTarget: EventTarget & HTMLFormElement}) {
    const response = await fetch("/api/user/logout", {method: 'POST'});
    
    if (response.status < 300) {
      goto('/');
    } else {
      alert("Logout failed");
    }
  }
</script>

<h1>{@html $LL.WELCOME()}</h1>
<p>{@html $LL.SUMMARY()}</p>
<p>Language: {$LL.LANGUAGE()}</p>
<p>Email: {userEmail}</p>
<p>Roles: {userRoles.join(", ")}</p>
{#if isLoggedIn}
  <form method="post" on:submit|preventDefault={logout}>
    <button>Log out</button>
  </form>
{:else}
  <form method="post" on:submit|preventDefault={loginOrSignup}>
    <div>
      <label for="email">Email</label>
      <input name="email" type="email">
    </div>
    <div>
      <label for="password">Password</label>
      <input name="password" type="password">
    </div>
    <button class="login-btn">Log in</button>
    <button class="register-btn">Register</button>
  </form>
{/if}