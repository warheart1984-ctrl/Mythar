import assert from "node:assert/strict";
import { mkdtempSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { test } from "node:test";
import { createMigrationEngine } from "../../src/core/migration/engine.js";

test("migration engine supports plan, verify, replay, rewind, and restore", () => {
  const root = mkdtempSync(join(tmpdir(), "ulx-migration-roundtrip-"));
  const engine = createMigrationEngine({ root });
  const runtime = engine.canonicalize({
    substrateId: "substrate-a",
    name: "Substrate A",
    evidence: [{ id: "evidence-1", kind: "migration.plan" }],
    lineage: ["origin"]
  });

  const snapshot = engine.plan(runtime);
  const applied = engine.apply(runtime, "evidence-2");
  const verified = engine.verify(applied);
  const replay = engine.replay("substrate-a");
  const rewind = engine.rewind("substrate-a");
  const restored = engine.restore(snapshot.snapshot_id);

  assert.equal(snapshot.substrate_id, "substrate-a");
  assert.equal(applied.phase, "applied");
  assert.equal(verified.valid, true);
  assert.equal(replay.steps.length >= 1, true);
  assert.equal(rewind.steps.length >= 1, true);
  assert.equal(restored.restored.runtime.status, "restored");
});
