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
      const res = await fetch('/api/user/me');
      if(res.status != 200) {
        user.update((u) => {
          u.is_checked = true;
          return u;
        });
        return;
      }
      const body = await res.json();
      let me: UserInfo = {
        user_id: body['id'],
        player_id: body['player_id'],
        name: null,
        country_code: null,
        discord_id: null,
        is_checked: true
      } 
      if(me.player_id === null) {
        user.set(me);
        return;
      }
      const res2 = await fetch(`/api/registry/players/${me.player_id}`);
      if(res2.status != 200) {
        user.set(me);
        return;
      }
      const body2 = await res2.json();
      me.name = body2['name'];
      me.country_code = body2['country_code'];
      me.discord_id = body2['discord_id'];
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