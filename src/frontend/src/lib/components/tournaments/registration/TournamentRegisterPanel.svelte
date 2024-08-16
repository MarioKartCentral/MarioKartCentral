<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import Section from '$lib/components/common/Section.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { page } from '$app/stores';
  import type { FriendCode } from '$lib/types/friend-code';
  import SoloSquadTournamentRegister from './SoloSquadTournamentRegister.svelte';
  import { onMount } from 'svelte';
  import type { MyTournamentRegistration } from '$lib/types/tournaments/my-tournament-registration';
  import MyRegistration from './MyRegistration.svelte';
  import TeamTournamentRegister from './TeamTournamentRegister.svelte';
  import { check_registrations_open } from '$lib/util/util';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';

  export let tournament: Tournament;

  let registration: MyTournamentRegistration;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  function get_game_fcs(game: string, fcs: FriendCode[]) {
    return fcs.filter((fc) => fc.game === game);
  }


  onMount(async () => {
    const res = await fetch(`/api/tournaments/${tournament.id}/myRegistration`);
    if (res.status === 200) {
      const body: MyTournamentRegistration = await res.json();
      registration = body;
      console.log(registration);
    }
  });
</script>

<Section header="Register">
  {#if registration}
    {#if user_info.player}
      <MyRegistration
        {registration}
        {tournament}
        friend_codes={get_game_fcs(tournament.game, user_info.player.friend_codes)}
      />
    {/if}
    {#if !check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true)}
      <div>
        You do not have permission to register for this tournament.
      </div>
    {:else}
      {#if tournament.teams_allowed && user_info.player}
        <TeamTournamentRegister {tournament} player={user_info.player} />
      {/if}
      {#if !registration.player}
        {#if !check_registrations_open(tournament)}
          <div>
            Registration for this tournament is closed.
          </div>
        {:else if user_info.player}
          <div>Want to register for this tournament? Just fill out your registration details below!</div>
          {#if get_game_fcs(tournament.game, user_info.player.friend_codes).length}
            {#if !tournament.teams_only}
              <SoloSquadTournamentRegister
                {tournament}
                friend_codes={get_game_fcs(tournament.game, user_info.player.friend_codes)}
              />
            {/if}
          {:else}
            <div>Please add an FC for {tournament.game} to register for this tournament.</div>
          {/if}
        {:else}
          <div>
            <a href="/{$page.params.lang}/player-signup"
              >Please complete your player registration to register for this tournament.</a
            >
          </div>
        {/if}
      {/if}
    {/if}
  {/if}
</Section>
