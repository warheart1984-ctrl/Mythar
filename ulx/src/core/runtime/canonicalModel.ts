import { createHash } from "crypto";

export type CanonicalRuntimePhase =
  | "census"
  | "planned"
  | "applied"
  | "verified"
  | "rewound"
  | "restored";

export interface CanonicalRuntimeEvidence {
  id: string;
  kind: string;
  path?: string;
  summary?: string;
}

export interface CanonicalRuntimeModel {
  id: string;
  substrateId: string;
  name: string;
  phase: CanonicalRuntimePhase;
  status: "draft" | "active" | "restored";
  evidence: CanonicalRuntimeEvidence[];
  lineage: string[];
  replayable: boolean;
  restorePointId?: string;
  updatedAt: string;
}

export interface CanonicalRuntimeInput {
  substrateId: string;
  name?: string;
  phase?: CanonicalRuntimePhase;
  status?: CanonicalRuntimeModel["status"];
  evidence?: CanonicalRuntimeEvidence[];
  lineage?: string[];
  replayable?: boolean;
  restorePointId?: string;
  updatedAt?: string;
}

function now(): string {
  return new Date().toISOString();
}

function stableId(parts: string[]): string {
  return createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 16);
}

export function canonicalizeRuntimeModel(input: CanonicalRuntimeInput): CanonicalRuntimeModel {
  const substrateId = input.substrateId.trim();
  const name = input.name?.trim() || substrateId;
  return {
    id: `runtime-${stableId([substrateId, name, input.phase ?? "applied"])}`,
    substrateId,
    name,
    phase: input.phase ?? "applied",
    status: input.status ?? "active",
    evidence: [...(input.evidence ?? [])],
    lineage: [...(input.lineage ?? [])],
    replayable: input.replayable ?? true,
    restorePointId: input.restorePointId,
    updatedAt: input.updatedAt ?? now()
  };
}

export function mergeCanonicalRuntimeModel(
  model: CanonicalRuntimeModel,
  patch: Partial<Omit<CanonicalRuntimeModel, "id" | "substrateId">>
): CanonicalRuntimeModel {
  return {
    ...model,
    ...patch,
    evidence: patch.evidence ? [...patch.evidence] : [...model.evidence],
    lineage: patch.lineage ? [...patch.lineage] : [...model.lineage],
    updatedAt: patch.updatedAt ?? now()
  };
}
