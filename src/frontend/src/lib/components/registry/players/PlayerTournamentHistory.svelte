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
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export let player: PlayerInfo;

  let mode: string | null = null;
  let game: string | null = null;
  let from: string | null = null;
  let to: string | null = null;

  let avatar_url = logo;
  if (player.user_settings && player.user_settings.avatar) {
    avatar_url = player.user_settings.avatar;
  }

  onMount(async () => {
  });

    async function fetchData() {
        // let url = `/api/registry/teams/transfers/${approval_status}?page=${page_number}`;
        let url = `/api/my_api_endpoint_lol`
        if(mode !== null) {
            url += `&mode=${mode}`;
        }
        if(from) {
            url += `&from_date=${new Date(from).getTime()/1000}`;
        }
        if(to) {
            url += `&to_date=${new Date(to).getTime()/1000}`;
        }
        const res = await fetch(url);
        if (res.status !== 200) {
            return;
  }

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
      <form on:submit|preventDefault={fetchData}>
        <div class="flex">
          <GameModeSelect bind:game bind:mode flex all_option hide_labels inline is_team />
          <Button type="submit">Filter</Button>
          <div class="option">
            <label for="from">From</label>
            <input name="from" type="datetime-local" bind:value={from} />
          </div>
          <div class="option">
            <label for="to">To</label>
            <input name="to" type="datetime-local" bind:value={to} />
          </div>
          <div class="option">
            <Button type="submit">Filter</Button>
          </div>
        </div>
      </form>
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
