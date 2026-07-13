import type { CanonicalRuntimeModel } from "../canonicalModel.js";
import { mergeCanonicalRuntimeModel } from "../canonicalModel.js";

export interface MigrationRestoreInput {
  runtime: CanonicalRuntimeModel;
  restorePointId: string;
  note?: string;
}

export function restoreMigration(input: MigrationRestoreInput): CanonicalRuntimeModel {
  return mergeCanonicalRuntimeModel(input.runtime, {
    phase: "restored",
    status: "restored",
    restorePointId: input.restorePointId,
    lineage: [...input.runtime.lineage, `restored:${input.restorePointId}`],
    evidence: [
      ...input.runtime.evidence,
      {
        id: input.restorePointId,
        kind: "migration.restore",
        summary: input.note ?? "restored runtime"
      }
    ]
  });
}
