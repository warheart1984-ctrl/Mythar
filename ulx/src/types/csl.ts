export type CslPrimitiveKind = "Atom" | "Struct" | "List" | "Map" | "Union" | "Option" | "Ref";

export type CslCosmogenicKind = "Being" | "Origin" | "Cycle" | "Transcendence" | "Cosmos";

export type CslArtifactKind = "Agent" | "Policy" | "Intent" | "Constraint" | "Decision";

export type CslRelationKind = "generates" | "resolves" | "governedBy" | "constrains" | "promotesTo" | "expandsTo";

export interface CslFieldDefinition {
  cslType: CslPrimitiveKind;
  semantic?: string;
  ref?: string;
}

export interface CslTypeDefinition {
  cslType: CslPrimitiveKind;
  name: string;
  kind?: CslCosmogenicKind;
  tier: number;
  status?: "draft" | "experimental" | "normative" | "informative" | "deprecated";
  classification?: "normative" | "informative";
  identity?: {
    stableId?: string;
    aliases?: string[];
  };
  authority?: {
    owner?: string;
    steward?: string;
    approval?: string[];
  };
  evidence?: {
    required?: string[];
    references?: string[];
  };
  provenance?: {
    source?: string;
    lineage?: string[];
    version?: string;
  };
  trust?: {
    level?: "low" | "medium" | "high";
    attestations?: string[];
  };
  traceability?: {
    matrixRefs?: string[];
    upstream?: string[];
    downstream?: string[];
  };
  conformance?: {
    requiredApis?: string[];
    requiredTests?: string[];
    standardsRefs?: string[];
    implementationProfiles?: string[];
  };
  version?: {
    semantic?: string;
    revision?: string;
    deprecatedBy?: string;
  };
  documentStatus?: {
    state?: "draft" | "review" | "approved" | "deprecated";
    lastReviewedAt?: string;
  };
  extensionPoints?: string[];
  fields?: Record<string, CslFieldDefinition>;
  dynamics?: {
    generates?: string[];
    resolves?: string[];
  };
  horizon?: {
    promotesTo?: string;
    expandsTo?: string[];
  };
}

export interface CslRuntimeAgent {
  id: string;
  role: string;
  capabilities: string[];
  tier?: number;
  promotes_to?: string;
}

export interface CslRuntimePolicy {
  id: string;
  name: string;
  version: string;
  rules: string[];
  enabled: boolean;
  tier?: number;
  promotes_to?: string;
  expands_to?: string[];
}

export interface CslRuntimeIntent {
  id: string;
  agent_id: string;
  kind: string;
  context: Record<string, unknown>;
  timestamp: string;
}

export interface CslRuntimeConstraint {
  id: string;
  policy_id: string;
  intent_id: string;
  rule: string;
  severity: "low" | "medium" | "high";
  timestamp: string;
}

export interface CslRuntimeDecision {
  id: string;
  intent_id: string;
  agent_id: string;
  policy_id: string;
  constraint_ids: string[];
  outcome: "accepted" | "blocked" | "escalated";
  evidence: Record<string, unknown>;
  timestamp: string;
  reason: string;
}

export interface CslArtifactRecord<TPayload extends object = object> {
  artifact_id: string;
  artifact_type: CslArtifactKind;
  cslType: CslPrimitiveKind;
  kind: CslCosmogenicKind;
  tier: number;
  name: string;
  payload: TPayload;
  relations: Record<CslRelationKind, string[]>;
  evolution: {
    promotesTo?: string;
    expandsTo: string[];
  };
  evidence: Record<string, unknown>;
  lineage: string[];
  created_at: string;
}

export interface CslLineageEdge {
  lineage_id: string;
  from: string;
  to: string;
  relation: CslRelationKind;
  artifact_id?: string;
  policy_version?: string;
  intent_id?: string;
  decision_id?: string;
  created_at: string;
  evidence?: Record<string, unknown>;
}

export interface CslReplayRecord {
  replay_id: string;
  policy_version: string;
  intent_id: string;
  decision_id: string;
  approved: boolean;
  outcome: string;
  notes: string[];
  timestamp: string;
}

export interface CslGraphNode {
  id: string;
  label: string;
  kind: CslArtifactKind | CslCosmogenicKind | string;
  tier: number;
}

export interface CslGraphEdge {
  from: string;
  to: string;
  type: CslRelationKind | string;
}

export interface CslGraph {
  nodes: CslGraphNode[];
  edges: CslGraphEdge[];
}

export interface CslEvidenceBundle {
  promotion_id: string;
  artifact: CslArtifactRecord | null;
  lineage: CslLineageEdge[];
  replay: CslReplayRecord[];
}

export interface CslAdapter {
  agent(agent: CslRuntimeAgent): CslArtifactRecord;
  policy(policy: CslRuntimePolicy): CslArtifactRecord;
  intent(intent: CslRuntimeIntent): CslArtifactRecord;
  constraint(constraint: CslRuntimeConstraint): CslArtifactRecord;
  decision(decision: CslRuntimeDecision): CslArtifactRecord;
}
