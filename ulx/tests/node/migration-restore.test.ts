import assert from "node:assert/strict";
import { mkdtempSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { test } from "node:test";
import { canonicalizeRuntimeModel } from "../../src/core/runtime/canonicalModel.js";
import { createMigrationSnapshot, writeMigrationSnapshot } from "../../src/core/migration/snapshot.js";
import { restoreMigration } from "../../src/core/migration/restore.js";

test("migration restore reloads a snapshot and marks it restored", () => {
  const root = mkdtempSync(join(tmpdir(), "ulx-migration-restore-"));
  const runtime = canonicalizeRuntimeModel({
    substrateId: "substrate-a",
    evidence: [{ id: "evidence-1", kind: "migration.plan" }],
    lineage: ["origin"]
  });
  const snapshot = writeMigrationSnapshot(root, createMigrationSnapshot(runtime, ["evidence-1"]));

  const restored = restoreMigration(root, snapshot.snapshot_id);

  assert.equal(restored.snapshot.snapshot_id, snapshot.snapshot_id);
  assert.equal(restored.restored.runtime.status, "restored");
  assert.equal(restored.restored.runtime.substrateId, "substrate-a");
});
