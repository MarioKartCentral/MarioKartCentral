<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import Section from "$lib/components/common/Section.svelte";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { page } from "$app/stores";
    import type { FriendCode } from "$lib/types/friend-code";
    import SoloSquadTournamentRegister from "./SoloSquadTournamentRegister.svelte";
    import { onMount } from "svelte";
    import type { MyTournamentRegistration } from "$lib/types/tournaments/my-tournament-registration";
    import MyRegistration from "./MyRegistration.svelte";
    import TeamTournamentRegister from "./TeamTournamentRegister.svelte";

    export let tournament: Tournament;

    let registration: MyTournamentRegistration;

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    function get_game_fcs(game: string, fcs: FriendCode[]) {
        return fcs.filter((fc) => fc.game === game);
    }

    function check_registrations_open() {
        if(!tournament.registrations_open) {
            return false;
        }
        let registration_deadline: Date | null = tournament.registration_deadline ? new Date(tournament.registration_deadline * 1000) : null;
        if(!registration_deadline) {
            return true;
        }
        let now = new Date().getTime();
        if (registration_deadline.getTime() < now) {
            return false;
        }
        return true;
    }

    

    onMount(async() => {
        const res = await fetch(`/api/tournaments/${tournament.id}/myRegistration`);
        if(res.status === 200) {
            const body: MyTournamentRegistration = await res.json();
            registration = body;
            console.log(registration);
        }
    });
</script>

<Section header="Register">
    {#if registration}
        {#if user_info.player}
            <MyRegistration {registration} {tournament} friend_codes={get_game_fcs(tournament.game, user_info.player.friend_codes)}/>
            {#if tournament.teams_allowed}
                <TeamTournamentRegister {tournament} player={user_info.player}/>
            {/if}
        {/if}
        {#if !registration.player}
            {#if !check_registrations_open()}
                Registration for this tournament is closed.
            {:else}
                {#if user_info.player}
                    <div>
                        Want to register for this tournament? Just fill out your registration details below!
                    </div>
                    
                    {#if get_game_fcs(tournament.game, user_info.player.friend_codes).length}
                        {#if !tournament.teams_only}
                            <SoloSquadTournamentRegister tournament={tournament} friend_codes={get_game_fcs(tournament.game, user_info.player.friend_codes)}/>
                        {/if}
                    {:else}
                        <div>Please add an FC for {tournament.game} to register for this tournament.</div>
                    {/if}
                    
                {:else}
                    <div><a href="/{$page.params.lang}/player-signup">Please complete your player registration to register for this tournament.</a></div>
                {/if}
            {/if}
        {/if}
    {/if}
</Section>