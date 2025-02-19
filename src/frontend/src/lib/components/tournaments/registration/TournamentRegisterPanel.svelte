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
  import ForceRegisterSoloSquad from './ForceRegisterSoloSquad.svelte';
  import LL from '$i18n/i18n-svelte';
  import { game_fc_types } from '$lib/util/util';

  export let tournament: Tournament;

  let registration: MyTournamentRegistration;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  function get_game_fcs(game: string, fcs: FriendCode[]) {
    return fcs.filter((fc) => fc.type === game_fc_types[game]);
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

<Section header={$LL.TOURNAMENTS.REGISTRATIONS.REGISTER()}>
  {#if registration}
    {#if user_info.player}
      <MyRegistration {registration} {tournament}/>
    {/if}
    {#if !check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true)}
      <div>
        {$LL.TOURNAMENTS.REGISTRATIONS.NO_PERMISSION_TO_REGISTER()}
      </div>
    {:else}
      {#if tournament.teams_allowed}
        <TeamTournamentRegister {tournament}/>
      {/if}
      {#if !registration.registrations.some((r) => !r.player.is_invite)}
        {#if !check_registrations_open(tournament)}
          <div>
            {$LL.TOURNAMENTS.REGISTRATIONS.REGISTRATIONS_CLOSED()}
          </div>
        {:else if user_info.player}
          {#if get_game_fcs(tournament.game, user_info.player.friend_codes).length}
            {#if !tournament.teams_only}
              <div>{$LL.TOURNAMENTS.REGISTRATIONS.REGISTER_PROMPT()}</div>
              <SoloSquadTournamentRegister
                {tournament}
                friend_codes={get_game_fcs(tournament.game, user_info.player.friend_codes)}
              />
            {/if}
          {:else}
            {$LL.TOURNAMENTS.REGISTRATIONS.ADD_FC_TO_REGISTER({game: tournament.game})}
          {/if}
        {:else}
          <div>
            <a href="/{$page.params.lang}/player-signup"
              >{$LL.TOURNAMENTS.REGISTRATIONS.COMPLETE_REGISTRATION_TO_REGISTER()}</a
            >
          </div>
        {/if}
      {/if}
    {/if}
  {/if}
  {#if check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations, tournament.id, tournament.series_id)}
    {#if !tournament.teams_only}
      <ForceRegisterSoloSquad {tournament}/>
    {/if}
    {#if tournament.teams_allowed}
      <TeamTournamentRegister {tournament} is_privileged={true}/>
    {/if}
  {/if}
</Section>
