import { createHash } from "crypto";
import type { CanonicalRuntimeEvidence } from "./canonicalModel.js";

export interface EvidenceLedgerEntry extends CanonicalRuntimeEvidence {
  recordedAt: string;
}

export interface EvidenceLedger {
  id: string;
  substrateId: string;
  entries: EvidenceLedgerEntry[];
  updatedAt: string;
}

function now(): string {
  return new Date().toISOString();
}

function stableId(parts: string[]): string {
  return createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 16);
}

export function createEvidenceLedger(substrateId: string, seed: CanonicalRuntimeEvidence[] = []): EvidenceLedger {
  return {
    id: `ledger-${stableId([substrateId])}`,
    substrateId,
    entries: seed.map((entry) => ({ ...entry, recordedAt: now() })),
    updatedAt: now()
  };
}

export function recordEvidence(ledger: EvidenceLedger, entry: CanonicalRuntimeEvidence): EvidenceLedger {
  return {
    ...ledger,
    entries: [...ledger.entries, { ...entry, recordedAt: now() }],
    updatedAt: now()
  };
}

export function summarizeEvidence(ledger: EvidenceLedger): string[] {
  return ledger.entries.map((entry) => `${entry.kind}:${entry.id}`);
}
