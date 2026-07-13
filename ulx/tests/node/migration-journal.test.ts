import assert from "node:assert/strict";
import { mkdtempSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { test } from "node:test";
import { appendMigrationJournalEntry, createMigrationJournal, readMigrationJournal } from "../../src/core/migration/journal.js";

test("migration journal appends and reads entries deterministically", () => {
  const root = mkdtempSync(join(tmpdir(), "ulx-migration-journal-"));
  const journal = createMigrationJournal(root);

  const first = appendMigrationJournalEntry(journal, "substrate-a", "census", { count: 1 });
  const second = appendMigrationJournalEntry(journal, "substrate-a", "apply", { runtime_id: "runtime-1" });

  const entries = readMigrationJournal(journal);

  assert.equal(entries.length, 2);
  assert.equal(entries[0]?.journal_id, first.journal_id);
  assert.equal(entries[1]?.journal_id, second.journal_id);
  assert.deepEqual(entries.map((entry) => entry.kind), ["census", "apply"]);
});
