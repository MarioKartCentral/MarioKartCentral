<script lang="ts">
  import '$lib/base.css'
  import { setLocale } from '$i18n/i18n-svelte';
  import NavBar from '$lib/components/NavBar.svelte';
  import type { LayoutData } from './$types';
  import Footer from '$lib/components/Footer.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from "$lib/types/user-info";
  import { onMount } from 'svelte';

  export let data : LayoutData;
  
  setLocale(data.locale);

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async() => {
    if(user_info.is_checked === false) {
      const res = await fetch('/api/user/me/player');
      if(res.status != 200) {
        user.update((u) => {
          u.is_checked = true;
          return u;
        });
        return;
      }
      const body = await res.json();
      let me: UserInfo = {
        id: body['id'],
        player_id: body['player_id'],
        player: body['player'],
        is_checked: true
      };
      user.set(me);
    }
  });

</script>

<header>
  <NavBar/>
</header>

<main>
  <slot/>
</main>

<footer>
  <Footer/>
</footer>

<style>
  main {
    flex: 1 0;
    padding: 30px 50px;
  }
</style>