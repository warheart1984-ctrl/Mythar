import assert from "node:assert/strict";
import { mkdtempSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { test } from "node:test";
import { appendMigrationJournalEntry, createMigrationJournal } from "../../src/core/migration/journal.js";
import { replayMigration } from "../../src/core/migration/replay.js";

test("migration replay preserves journal order and provenance", () => {
  const root = mkdtempSync(join(tmpdir(), "ulx-migration-replay-"));
  const journal = createMigrationJournal(root);
  appendMigrationJournalEntry(journal, "substrate-a", "census", { count: 1 });
  appendMigrationJournalEntry(journal, "substrate-a", "apply", { runtime_id: "runtime-1" });

  const replay = replayMigration(journal, "substrate-a");

  assert.equal(replay.steps.length, 2);
  assert.equal(replay.steps[0]?.step, "1:census");
  assert.equal(replay.steps[1]?.step, "2:apply");
  assert.equal(replay.substrateId, "substrate-a");
});
