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
  import Button from '$lib/components/common/buttons/Button.svelte';

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
    }
  });
</script>

<Section header={$LL.TOURNAMENTS.REGISTRATIONS.REGISTER()}>
  {#if user_info.id === null}
    <div>
      <Button href="/{$page.params.lang}/user/login">
        {$LL.TOURNAMENTS.REGISTRATIONS.SIGN_IN_REGISTER_TO_REGISTER()}
      </Button>
    </div>
  {:else if !user_info.email_confirmed}
    <div>
      <Button href="/{$page.params.lang}/user/confirm-email">
        {$LL.TOURNAMENTS.REGISTRATIONS.CONFIRM_EMAIL_TO_REGISTER()}
      </Button>
    </div>
  {:else if user_info.player === null}
    <div>
      <Button href="/{$page.params.lang}/user/player-signup"
        >{$LL.TOURNAMENTS.REGISTRATIONS.COMPLETE_REGISTRATION_TO_REGISTER()}</Button
      >
    </div>
  {:else if user_info.player.discord === null}
    <div>
      <Button href="/{$page.params.lang}/registry/players/edit-profile">
        {$LL.TOURNAMENTS.REGISTRATIONS.LINK_DISCORD_TO_REGISTER()}
      </Button>
    </div>
  {:else if registration}
    <MyRegistration {registration} {tournament}/>
    {#if !check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true)}
      <div>
        {$LL.TOURNAMENTS.REGISTRATIONS.NO_PERMISSION_TO_REGISTER()}
      </div>
    {:else}
      {#if check_registrations_open(tournament)}
        {#if tournament.teams_allowed}
          <TeamTournamentRegister {tournament}/>
        {/if}
        {#if !tournament.teams_only && !registration.registrations.some((r) => !r.is_invite)}
          {#if get_game_fcs(tournament.game, user_info.player.friend_codes).length}
            <div>{$LL.TOURNAMENTS.REGISTRATIONS.REGISTER_PROMPT()}</div>
            <SoloSquadTournamentRegister
              {tournament}
              friend_codes={get_game_fcs(tournament.game, user_info.player.friend_codes)}
            />
          {:else}
            {$LL.TOURNAMENTS.REGISTRATIONS.ADD_FC_TO_REGISTER({game: tournament.game})}
          {/if}
        {/if}
      {:else}
        <div>
          {$LL.TOURNAMENTS.REGISTRATIONS.REGISTRATIONS_CLOSED()}
        </div>
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