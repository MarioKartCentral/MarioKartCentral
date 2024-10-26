<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { UserInfo } from '$lib/types/user-info';
  import Section from '$lib/components/common/Section.svelte';
  import logo from '$lib/assets/logo.png';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import { Avatar } from 'flowbite-svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import DiscordDisplay from '$lib/components/common/discord/DiscordDisplay.svelte';
  import { game_order } from '$lib/util/util';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export let player: PlayerInfo;

  let avatar_url = logo;
  if (player.user_settings && player.user_settings.avatar) {
    avatar_url = player.user_settings.avatar;
  }

  onMount(async () => {
    // Somehow get all tournaments, where player.id exists
    // FFA tournaments and Team tournaments are different objects


    // let param_id = $page.url.searchParams.get('id');
    // id = Number(param_id);
    // const res = await fetch(`/api/registry/players/${id}`);
    // if (res.status != 200) {
    //   player_found = false;
    //   return;
    // }
    // const body: PlayerInfo = await res.json();
    // player = body;

    // if (player.ban_info) {
    //   // fetch detailed ban info. api will only return successfully if the user is a mod
    //   const res2 = await fetch(`/api/registry/players/bans?player_id=${player.id}`);
    //   if (res2.status === 200) {
    //     const data: BanListData = await res2.json();
    //     if (data.ban_count === 1) banInfo = data.ban_list[0];
    //   }
    // }
  });

  // Function to filter data for specific game
  // Function to filter data for specific mode
  // Function to sort data by tournament date
  // Function to sort data by tournament name
  // Function to sort data by result
  console.log(player);
</script>

<Section header={$LL.PLAYER_TOURNAMENT_HISTORY.TOURNAMENT_HISTORY()}>
  <div>
    Game
    <div>
      <div>Mode</div>
      <div>Sort</div>
      <div>___</div>
      <div>FFA Tournaments</div>
      <div>Tournament Name | Result</div>
      <div>table...</div>
      <div>___</div>
      <div>Team Tournaments</div>
      <div>Tournament Name | Result</div>
      <div>table...</div>
    </div>
  </div>
</Section>
