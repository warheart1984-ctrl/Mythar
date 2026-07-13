import assert from "node:assert/strict";
import { mkdtempSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { test } from "node:test";
import { appendMigrationJournalEntry, createMigrationJournal } from "../../src/core/migration/journal.js";
import { rewindMigration } from "../../src/core/migration/rewind.js";

test("migration rewind reverses the replay order", () => {
  const root = mkdtempSync(join(tmpdir(), "ulx-migration-rewind-"));
  const journal = createMigrationJournal(root);
  appendMigrationJournalEntry(journal, "substrate-a", "census", { count: 1 });
  appendMigrationJournalEntry(journal, "substrate-a", "apply", { runtime_id: "runtime-1" });

  const rewind = rewindMigration(journal, "substrate-a");

  assert.equal(rewind.steps.length, 2);
  assert.equal(rewind.steps[0]?.kind, "apply");
  assert.equal(rewind.steps[1]?.kind, "census");
  assert.equal(rewind.substrateId, "substrate-a");
});
