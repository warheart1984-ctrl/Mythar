export type AaisCapabilityKind =
  | "engine"
  | "generator"
  | "registry"
  | "dashboard"
  | "verifier"
  | "agent"
  | "optimizer"
  | "orchestrator"
  | "loader"
  | "scheduler"
  | "analyzer"
  | "ledger"
  | "graph"
  | "database";

export type AaisPreferredModel = "qwen-3b" | "qwen-7b";

export interface AaisRoutingHint {
  preferredModel?: AaisPreferredModel;
  reason?: string;
}

export interface AaisCapabilityDescriptor {
  id: string;
  name: string;
  kind: AaisCapabilityKind;
  summary: string;
}

export interface AaisCodingCapability {
  id: string;
  name: string;
  description: string;
  inputs: readonly string[];
  governanceConstraints: readonly string[];
  routing: Partial<Record<string, AaisRoutingHint>>;
}

export interface AaisCodingProvenanceRecord {
  capabilityName: string;
  filesChanged: readonly string[];
  testsRan: readonly string[];
  model: AaisPreferredModel;
  constraintsApplied: readonly string[];
  evidence: readonly string[];
}

export interface AaisCodingProvenanceGraph {
  records: readonly AaisCodingProvenanceRecord[];
}

export interface AaisConsoleProjection {
  capabilities: readonly AaisCapabilityDescriptor[];
  codingCapabilities: readonly AaisCodingCapability[];
  provenance: AaisCodingProvenanceGraph;
}

export interface AaisConsoleProvider {
  listCapabilities(): readonly AaisCapabilityDescriptor[];
  listCodingCapabilities(): readonly AaisCodingCapability[];
  listProvenanceRecords(): readonly AaisCodingProvenanceRecord[];
}
