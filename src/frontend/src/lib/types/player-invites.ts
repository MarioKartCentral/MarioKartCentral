import type { TeamInvite } from "./team-invite";
import type { TournamentInvite } from "./tournament-invite";

export type PlayerInvites = {
    player_id: number;
    team_invites: TeamInvite[];
    tournament_invites: TournamentInvite[];
};