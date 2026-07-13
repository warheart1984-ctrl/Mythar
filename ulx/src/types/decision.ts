export type DecisionType = "promote" | "deprecate" | "modify-contract" | "rollback";

export interface Decision {
  decision_id: string;
  substrate_id: string;
  type: DecisionType;
  actor: string;
  target_status?: string;
  reason?: string;
  timestamp: string;
}

export interface DecisionResult {
  approved: boolean;
  error?: string;
}

