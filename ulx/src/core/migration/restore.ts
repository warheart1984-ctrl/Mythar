import type { MigrationSnapshot } from "./snapshot.js";
import { readMigrationSnapshot, writeMigrationSnapshot } from "./snapshot.js";

export interface MigrationRestoreResult {
  snapshot: MigrationSnapshot;
  restored: MigrationSnapshot;
}

export function restoreMigration(root: string, snapshotId: string): MigrationRestoreResult {
  const snapshot = readMigrationSnapshot(root, snapshotId);
  if (!snapshot) {
    throw new Error(`snapshot not found: ${snapshotId}`);
  }
  const restored: MigrationSnapshot = {
    ...snapshot,
    runtime: {
      ...snapshot.runtime,
      status: "restored",
      updatedAt: new Date().toISOString()
    }
  };
  writeMigrationSnapshot(root, restored);
  return { snapshot, restored };
}
