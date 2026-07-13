import { createHash } from "crypto";
import type { CanonicalRuntimeModel } from "./canonicalModel.js";
import { createRestorePoint, restoreFromPoint, type RuntimeRestorePoint } from "./restorePoint.js";

export interface RuntimeCutoverPlan {
  id: string;
  substrateId: string;
  from: CanonicalRuntimeModel;
  to: CanonicalRuntimeModel;
  restorePoint: RuntimeRestorePoint;
  gates: string[];
  rollback: string[];
  createdAt: string;
}

function now(): string {
  return new Date().toISOString();
}

function stableId(parts: string[]): string {
  return createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 16);
}

export function buildCutoverPlan(
  from: CanonicalRuntimeModel,
  to: CanonicalRuntimeModel,
  gates: string[] = []
): RuntimeCutoverPlan {
  const restorePoint = createRestorePoint(from, "pre-cutover");
  return {
    id: `cutover-${stableId([from.id, to.id, from.substrateId])}`,
    substrateId: from.substrateId,
    from: {
      ...from,
      evidence: [...from.evidence],
      lineage: [...from.lineage]
    },
    to: {
      ...to,
      evidence: [...to.evidence],
      lineage: [...to.lineage]
    },
    restorePoint,
    gates: [...gates],
    rollback: [restorePoint.id, from.id],
    createdAt: now()
  };
}

export function rewindCutover(plan: RuntimeCutoverPlan): CanonicalRuntimeModel {
  return restoreFromPoint(plan.restorePoint);
}
