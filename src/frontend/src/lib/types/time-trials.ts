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
  player_name: string; // Added
  player_country_code: string; // Added
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

export interface PropertyValidationStatusData {
  property_name: string;
  is_validated: boolean;
  is_valid: boolean | null;
  validated_by_player_id: string | null;
  validated_at: string | null; // ISO date string
}

export interface ProofData {
  url?: string;
  type?: string;
  // other properties from the actual proof_data JSON
  [key: string]: unknown; // Allow other properties
}

export interface ProofWithValidationStatusResponseData {
  id: string;
  time_trial_id: string;
  player_id: string;
  player_name?: string | null;
  player_country_code?: string | null;
  game: string;
  proof_data: ProofData | null;
  properties: string[];
  created_at: string; // ISO date string
  validation_statuses: PropertyValidationStatusData[];
  // Time trial data for displaying values to verify
  track?: string | null;
  time_ms?: number | null;
  time_trial_data?: Record<string, unknown> | null;
}

export interface PropertyValidationData {
  property_name: string;
  is_valid: boolean;
}

export interface ErrorResponse {
  detail: string;
}
