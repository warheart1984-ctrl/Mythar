import type { MigrationJournal, MigrationJournalEntry } from "./journal.js";
import { readMigrationJournal } from "./journal.js";

export interface MigrationReplayStep {
  step: string;
  entry: MigrationJournalEntry;
}

export interface MigrationReplayResult {
  journal: MigrationJournal;
  substrateId: string;
  steps: MigrationReplayStep[];
}

export function replayMigration(journal: MigrationJournal, substrateId?: string): MigrationReplayResult {
  const entries = readMigrationJournal(journal).filter((entry) =>
    substrateId ? entry.substrate_id === substrateId : true
  );
  const steps = entries.map((entry, index) => ({
    step: `${index + 1}:${entry.kind}`,
    entry
  }));
  return {
    journal,
    substrateId: substrateId ?? entries[0]?.substrate_id ?? "",
    steps
  };
}
