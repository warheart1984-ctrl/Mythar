import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { createHash } from "crypto";
import type { CanonicalRuntimeModel } from "../runtime/canonicalModel.js";

export interface MigrationSnapshot {
  snapshot_id: string;
  substrate_id: string;
  phase: string;
  runtime: CanonicalRuntimeModel;
  evidence: string[];
  replayable: boolean;
  created_at: string;
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

export function createMigrationSnapshot(runtime: CanonicalRuntimeModel, evidence: string[] = []): MigrationSnapshot {
  return {
    snapshot_id: `snapshot-${stableId([runtime.substrateId, runtime.id, runtime.phase])}`,
    substrate_id: runtime.substrateId,
    phase: runtime.phase,
    runtime: {
      ...runtime,
      evidence: [...runtime.evidence],
      lineage: [...runtime.lineage]
    },
    evidence: [...evidence],
    replayable: runtime.replayable,
    created_at: now()
  };
}

export function writeMigrationSnapshot(root: string, snapshot: MigrationSnapshot): MigrationSnapshot {
  const path = join(root, "snapshots", `${snapshot.snapshot_id}.json`);
  ensureDirectory(path);
  writeFileSync(path, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
  return snapshot;
}

export function readMigrationSnapshot(root: string, snapshotId: string): MigrationSnapshot | null {
  const path = join(root, "snapshots", `${snapshotId}.json`);
  if (!existsSync(path)) {
    return null;
  }
  return JSON.parse(readFileSync(path, "utf8")) as MigrationSnapshot;
}
