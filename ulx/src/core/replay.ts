import { existsSync, readFileSync } from "fs";
import { readJson } from "./fs.js";
import type { ContinuityEvent } from "../types/ciems.js";
import { createAndBroadcastUlxEvent } from "../daemon/events.js";

export interface ReplaySummary {
  substrate_id: string;
  from: "origin" | "import" | "normalized";
  to: "current";
  steps: string[];
}

function readLogEntries(substrateId: string): Array<Record<string, unknown>> {
  const path = `logs/governance/${substrateId}.log.jsonl`;
  if (!existsSync(path)) {
    return [];
  }
  return readFileSync(path, "utf8")
    .split("\n")
    .map((line: string) => line.trim())
    .filter(Boolean)
    .map((line: string) => JSON.parse(line));
}

export function replay(
  substrateId: string,
  from: "origin" | "import" | "normalized",
  to: "current"
): ReplaySummary {
  const substrate = readJson<{ status?: string; lineage?: Record<string, unknown> }>(
    `substrates/${substrateId}/substrate.json`
  );
  const continuity = readJson<{ timeline: ContinuityEvent[] }>(
    `constitutional/continuity/${substrateId}.continuity.json`
  );
  const steps = [
    `substrate:${substrate.status ?? "unknown"}`,
    ...continuity.timeline.map((event: ContinuityEvent) => `${event.type}:${event.timestamp}`),
    ...readLogEntries(substrateId).map((event: Record<string, unknown>) => `decision:${String(event.result ?? "unknown")}`)
  ];
  for (const step of steps) {
    createAndBroadcastUlxEvent(substrateId, "replay.step", { step, status: "ok" }, new Date().toISOString());
  }
  createAndBroadcastUlxEvent(
    substrateId,
    "replay.complete",
    {
      steps,
      duration_ms: Math.max(steps.length * 5, 0)
    },
    new Date().toISOString()
  );
  return { substrate_id: substrateId, from, to, steps };
}
