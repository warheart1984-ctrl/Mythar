import { existsSync, readFileSync } from "fs";
import { join } from "path";
import { applyMigration } from "../runtime/migration/apply.js";
import { canonicalizeRuntimeModel, type CanonicalRuntimeInput, type CanonicalRuntimeModel } from "../runtime/canonicalModel.js";
import { censusSubstrates, type MigrationCensusResult } from "../runtime/migration/census.js";
import { rewindMigration as rewindRuntimeMigration } from "../runtime/migration/rewind.js";
import { restoreMigration as restoreRuntimeMigration } from "../runtime/migration/restore.js";
import { verifyMigration } from "../runtime/migration/verify.js";
import {
  appendMigrationJournalEntry,
  createMigrationJournal,
  readMigrationJournal,
  type MigrationJournal,
  type MigrationJournalEntry
} from "./journal.js";
import { createMigrationSnapshot, readMigrationSnapshot, writeMigrationSnapshot, type MigrationSnapshot } from "./snapshot.js";
import { replayMigration, type MigrationReplayResult } from "./replay.js";
import { rewindMigration as rewindJournal, type MigrationRewindResult } from "./rewind.js";
import { restoreMigration as restoreJournal, type MigrationRestoreResult } from "./restore.js";

export interface MigrationEngineOptions {
  root?: string;
}

export interface MigrationConformanceBundle {
  schema: object;
  conformance: object;
  replay: object;
  restore: object;
  timeline: object;
}

export class MigrationEngine {
  private readonly root: string;
  private readonly journal: MigrationJournal;

  constructor(options: MigrationEngineOptions = {}) {
    this.root = options.root ?? "ulx/.ulx-migration";
    this.journal = createMigrationJournal(this.root);
  }

  census(root = "substrates"): MigrationCensusResult {
    return censusSubstrates(root);
  }

  canonicalize(input: CanonicalRuntimeInput): CanonicalRuntimeModel {
    return canonicalizeRuntimeModel(input);
  }

  plan(runtime: CanonicalRuntimeModel): MigrationSnapshot {
    const snapshot = createMigrationSnapshot(runtime, runtime.evidence.map((entry) => entry.id));
    writeMigrationSnapshot(this.root, snapshot);
    appendMigrationJournalEntry(this.journal, runtime.substrateId, "census", {
      snapshot_id: snapshot.snapshot_id,
      phase: snapshot.phase
    });
    return snapshot;
  }

  apply(runtime: CanonicalRuntimeModel, evidenceId = "evidence-apply"): CanonicalRuntimeModel {
    const next = applyMigration({ runtime, evidenceId, note: "migration engine apply" });
    appendMigrationJournalEntry(this.journal, runtime.substrateId, "apply", {
      runtime_id: next.id,
      phase: next.phase
    });
    return next;
  }

  verify(runtime: CanonicalRuntimeModel): ReturnType<typeof verifyMigration> {
    const result = verifyMigration(runtime);
    appendMigrationJournalEntry(this.journal, runtime.substrateId, "verify", result);
    return result;
  }

  replay(substrateId?: string): MigrationReplayResult {
    return replayMigration(this.journal, substrateId);
  }

  rewind(substrateId?: string): MigrationRewindResult {
    const journalResult = rewindJournal(this.journal, substrateId);
    appendMigrationJournalEntry(this.journal, journalResult.substrateId || "unknown", "rewind", {
      steps: journalResult.steps.length
    });
    return journalResult;
  }

  restore(snapshotId: string): MigrationRestoreResult {
    const restored = restoreJournal(this.root, snapshotId);
    appendMigrationJournalEntry(this.journal, restored.restored.substrate_id, "restore", {
      snapshot_id: snapshotId
    });
    return restored;
  }

  restoreRuntime(runtime: CanonicalRuntimeModel, restorePointId: string): CanonicalRuntimeModel {
    const restored = restoreRuntimeMigration({ runtime, restorePointId });
    appendMigrationJournalEntry(this.journal, runtime.substrateId, "restore", {
      restorePointId,
      runtime_id: restored.id
    });
    return restored;
  }

  rewindRuntime(runtime: CanonicalRuntimeModel, reason?: string): CanonicalRuntimeModel {
    return rewindRuntimeMigration({ runtime, reason });
  }

  getJournalEntries(): MigrationJournalEntry[] {
    return readMigrationJournal(this.journal);
  }

  getSnapshot(snapshotId: string): MigrationSnapshot | null {
    return readMigrationSnapshot(this.root, snapshotId);
  }

  loadConformanceBundle(): MigrationConformanceBundle {
    const base = "ulx/constitutional";
    return {
      schema: existsSync(join(base, "migration.schema.json"))
        ? JSON.parse(readFileSync(join(base, "migration.schema.json"), "utf8"))
        : {},
      conformance: existsSync(join(base, "migration.conformance.json"))
        ? JSON.parse(readFileSync(join(base, "migration.conformance.json"), "utf8"))
        : {},
      replay: existsSync(join(base, "migration.replay.conformance.json"))
        ? JSON.parse(readFileSync(join(base, "migration.replay.conformance.json"), "utf8"))
        : {},
      restore: existsSync(join(base, "migration.restore.conformance.json"))
        ? JSON.parse(readFileSync(join(base, "migration.restore.conformance.json"), "utf8"))
        : {},
      timeline: existsSync(join(base, "migration.timeline.conformance.json"))
        ? JSON.parse(readFileSync(join(base, "migration.timeline.conformance.json"), "utf8"))
        : {}
    };
  }
}

export function createMigrationEngine(options: MigrationEngineOptions = {}): MigrationEngine {
  return new MigrationEngine(options);
}
