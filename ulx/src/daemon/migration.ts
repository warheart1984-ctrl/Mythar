import { readFileSync } from "fs";
import type { IncomingMessage, ServerResponse } from "http";
import { createMigrationEngine } from "../core/migration/engine.js";

async function readBody(req: IncomingMessage): Promise<string> {
  return await new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk: Buffer) => chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function json(res: ServerResponse, statusCode: number, payload: unknown): void {
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json");
  res.end(JSON.stringify(payload));
}

export async function handleMigrationRequest(req: IncomingMessage, res: ServerResponse): Promise<boolean> {
  if (!req.url || !req.url.startsWith("/migration")) {
    return false;
  }

  const engine = createMigrationEngine();
  if (req.method === "GET") {
    json(res, 200, {
      ok: true,
      journal: engine.getJournalEntries(),
      conformance: engine.loadConformanceBundle()
    });
    return true;
  }

  if (req.method === "POST") {
    const body = await readBody(req);
    const parsed = JSON.parse(body) as {
      substrateId: string;
      runtimeJson?: string;
      snapshotId?: string;
      operation?: "plan" | "verify" | "replay" | "rewind" | "restore";
    };
    if (parsed.operation === "restore" && parsed.snapshotId) {
      json(res, 200, engine.restore(parsed.snapshotId));
      return true;
    }
    if (parsed.runtimeJson) {
      const runtime = JSON.parse(readFileSync(parsed.runtimeJson, "utf8")) as { substrateId: string };
      json(res, 200, engine.plan(engine.canonicalize(runtime)));
      return true;
    }
    json(res, 200, {
      ok: true,
      census: engine.census(),
      substrateId: parsed.substrateId
    });
    return true;
  }

  json(res, 405, { ok: false, error: "method not allowed" });
  return true;
}
