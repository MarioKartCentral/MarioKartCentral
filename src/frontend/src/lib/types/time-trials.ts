export interface ProofRequestData {
  url: string;
  type: string;
}

export interface Proof {
  id: string;
  url: string;
  type: string;
  created_at: string;
  status: "valid" | "invalid" | "unvalidated";
  validator_id?: number | null;
  validated_at?: string | null;
}

export interface TimeTrial {
  id: string;
  version: number;
  player_id: string;
  game: string;
  track: string;
  time_ms: number;
  proofs: Proof[];
  created_at: string;
  updated_at: string;
  player_name?: string | null;
  player_country_code?: string | null;
  validation_status: "valid" | "invalid" | "unvalidated" | "proofless";
}

export interface TimeTrialListResponse {
  records: TimeTrial[];
}

export interface ProofWithValidationStatusResponseData {
  id: string;
  time_trial_id: string;
  player_id: string;
  game: string;
  proof_data: ProofRequestData | null;
  created_at: string; // ISO date string
  track: string;
  time_ms: number;
  version: number;
  player_name?: string | null;
  player_country_code?: string | null;
}

export interface ErrorResponse {
  detail: string;
}

export interface EditProofData {
  id?: string | null; // None for new proofs
  url: string;
  type: string;
  status?: string | null; // Only editable by validators
  deleted?: boolean; // Mark for deletion
}

export interface EditTimeTrialRequestData {
  game: string;
  track: string;
  time_ms: number;
  proofs: EditProofData[];
  version: number;
  player_id?: number | null; // Only editable by validators
  is_invalid?: boolean | null; // Only editable by validators
}
