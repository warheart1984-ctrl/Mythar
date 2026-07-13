import type { CanonicalRuntimeModel } from "../canonicalModel.js";

export interface MigrationVerificationResult {
  valid: boolean;
  issues: string[];
}

export function verifyMigration(runtime: CanonicalRuntimeModel): MigrationVerificationResult {
  const issues: string[] = [];
  if (!runtime.id.trim()) {
    issues.push("missing runtime id");
  }
  if (!runtime.substrateId.trim()) {
    issues.push("missing substrate id");
  }
  if (runtime.evidence.length === 0) {
    issues.push("missing evidence");
  }
  if (runtime.lineage.length === 0) {
    issues.push("missing lineage");
  }
  return {
    valid: issues.length === 0,
    issues
  };
}
