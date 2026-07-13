export interface Intent {
  substrate_id: string;
  intent: string;
  timestamp: string;
}

export interface Evidence {
  substrate_id: string;
  sources: unknown[];
  artifacts: unknown[];
  lineage: Record<string, unknown>;
  verification: Record<string, unknown>;
  integrity: Record<string, unknown>;
}

export interface Authority {
  substrate_id: string;
  actors: { id: string; role: string }[];
  mandate: string;
  scope: {
    domains: string[];
    operations: string[];
  };
}

export interface ContinuityEvent {
  event_id: string;
  type: string;
  timestamp: string;
  details?: string;
}

export interface Continuity {
  substrate_id: string;
  timeline: ContinuityEvent[];
  dependencies: unknown[];
  breaks: unknown[];
  resolutions: unknown[];
}

export interface Substrate {
  id: string;
  domain: string;
  layer: string;
  status: string;
}

