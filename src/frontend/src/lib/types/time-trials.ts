/**
 * Time trials types for frontend
 */

export interface TimeTrialData {
    lap_times: number[];
    character: string;
    kart: string;
}

export interface MK8DXTimeTrialData extends TimeTrialData {
    tires: string;
    glider: string;
    cc: number;
}

export interface MKWorldTimeTrialData extends TimeTrialData {
    // No additional properties for now
}

export interface TimeTrial {
    id: string;
    version: number;
    player_id: string;
    game: string;
    track: string;
    time_ms: number;
    data: TimeTrialData | MK8DXTimeTrialData | MKWorldTimeTrialData;
    created_at: string;
    updated_at: string;
}

export interface TimeTrialListResponse {
    time_trials: TimeTrial[];
    total_count?: number;
}

export interface TimeTrialLeaderboardEntry {
    id: string;
    player_id: string;
    time_ms: number;
    data: TimeTrialData | MK8DXTimeTrialData | MKWorldTimeTrialData;
    created_at: string;
}
