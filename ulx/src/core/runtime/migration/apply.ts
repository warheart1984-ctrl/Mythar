import type { CanonicalRuntimeModel } from "../canonicalModel.js";
import { mergeCanonicalRuntimeModel } from "../canonicalModel.js";

export interface MigrationApplyInput {
  runtime: CanonicalRuntimeModel;
  evidenceId: string;
  note: string;
}

export function applyMigration(input: MigrationApplyInput): CanonicalRuntimeModel {
  const next = mergeCanonicalRuntimeModel(input.runtime, {
    phase: "applied",
    status: "active",
    evidence: [
      ...input.runtime.evidence,
      {
        id: input.evidenceId,
        kind: "migration.apply",
        summary: input.note
      }
    ],
    lineage: [...input.runtime.lineage, `applied:${input.evidenceId}`]
  });
  return next;
}
