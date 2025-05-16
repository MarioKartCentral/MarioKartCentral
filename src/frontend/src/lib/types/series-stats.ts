import type { PlayerBasic } from "./player";
import type { RosterBasic } from "./roster-basic";

export type SeriesStats = {
    gold: number;
    silver: number;
    bronze: number;
    appearances: number;
    medals_placement: number;
    appearances_placement: number;
}

export type PlayerSeriesStats = PlayerBasic & SeriesStats;
export type RosterSeriesStats = RosterBasic & SeriesStats;

export type CombinedSeriesStats = {
    player_stats: PlayerSeriesStats[];
    roster_stats: RosterSeriesStats[];
}

export type Medals = {
    gold: number;
    silver: number;
    bronze: number;
}