import type { CanonicalRuntimeModel } from "../canonicalModel.js";
import { mergeCanonicalRuntimeModel } from "../canonicalModel.js";

export interface MigrationRewindInput {
  runtime: CanonicalRuntimeModel;
  reason?: string;
}

export function rewindMigration(input: MigrationRewindInput): CanonicalRuntimeModel {
  return mergeCanonicalRuntimeModel(input.runtime, {
    phase: "rewound",
    status: "active",
    lineage: [...input.runtime.lineage, `rewound:${input.reason ?? "rollback"}`],
    evidence: [
      ...input.runtime.evidence,
      {
        id: `rewind-${input.runtime.id}`,
        kind: "migration.rewind",
        summary: input.reason ?? "rewind applied"
      }
    ]
  });
}
