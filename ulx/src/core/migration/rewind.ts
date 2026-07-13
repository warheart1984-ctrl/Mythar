import type { MigrationJournal, MigrationJournalEntry } from "./journal.js";
import { readMigrationJournal } from "./journal.js";

export interface MigrationRewindResult {
  journal: MigrationJournal;
  substrateId: string;
  steps: MigrationJournalEntry[];
}

export function rewindMigration(journal: MigrationJournal, substrateId?: string): MigrationRewindResult {
  const entries = readMigrationJournal(journal)
    .filter((entry) => (substrateId ? entry.substrate_id === substrateId : true))
    .reverse();
  return {
    journal,
    substrateId: substrateId ?? entries[0]?.substrate_id ?? "",
    steps: entries
  };
}
