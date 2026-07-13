import { appendFileSync, existsSync, mkdirSync, readFileSync } from "fs";
import { dirname, join } from "path";
import { createHash } from "crypto";

export type MigrationJournalKind = "census" | "apply" | "verify" | "rewind" | "restore";

export interface MigrationJournalEntry {
  journal_id: string;
  substrate_id: string;
  kind: MigrationJournalKind;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface MigrationJournal {
  root: string;
  path: string;
}

function ensureDirectory(path: string): void {
  const dir = dirname(path);
  if (dir && !existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function now(): string {
  return new Date().toISOString();
}

function stableId(parts: string[]): string {
  return createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 16);
}

export function createMigrationJournal(root = "ulx/.ulx-migration"): MigrationJournal {
  return {
    root,
    path: join(root, "journal.jsonl")
  };
}

export function readMigrationJournal(journal: MigrationJournal): MigrationJournalEntry[] {
  if (!existsSync(journal.path)) {
    return [];
  }
  const raw = readFileSync(journal.path, "utf8").trim();
  if (!raw) {
    return [];
  }
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line) as MigrationJournalEntry)
    .sort((left, right) => left.created_at.localeCompare(right.created_at));
}

export function appendMigrationJournalEntry(
  journal: MigrationJournal,
  substrateId: string,
  kind: MigrationJournalKind,
  payload: Record<string, unknown>
): MigrationJournalEntry {
  const entry: MigrationJournalEntry = {
    journal_id: `journal-${stableId([journal.root, substrateId, kind, JSON.stringify(payload)])}`,
    substrate_id: substrateId,
    kind,
    payload: { ...payload },
    created_at: now()
  };
  ensureDirectory(journal.path);
  appendFileSync(journal.path, `${JSON.stringify(entry)}\n`, "utf8");
  return entry;
}
