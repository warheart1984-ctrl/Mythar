import { createHash } from "crypto";
import type { CanonicalRuntimeModel } from "./canonicalModel.js";

export interface RuntimeRestorePoint {
  id: string;
  substrateId: string;
  label: string;
  createdAt: string;
  runtime: CanonicalRuntimeModel;
}

function now(): string {
  return new Date().toISOString();
}

function stableId(parts: string[]): string {
  return createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 16);
}

export function createRestorePoint(runtime: CanonicalRuntimeModel, label: string): RuntimeRestorePoint {
  return {
    id: `restore-${stableId([runtime.substrateId, runtime.id, label])}`,
    substrateId: runtime.substrateId,
    label,
    createdAt: now(),
    runtime: {
      ...runtime,
      evidence: [...runtime.evidence],
      lineage: [...runtime.lineage]
    }
  };
}

export function restoreFromPoint(point: RuntimeRestorePoint): CanonicalRuntimeModel {
  return {
    ...point.runtime,
    evidence: [...point.runtime.evidence],
    lineage: [...point.runtime.lineage],
    restorePointId: point.id,
    status: "restored",
    updatedAt: now()
  };
}
